package main

import (
	"log"
	"fmt"
	"os"
	"path"
	"net/http"
	"time"
	"strings"

	"github.com/jlaffaye/ftp"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/robfig/cron/v3"

	"gitlab-k8s.wzs.wistron.com.cn/aoi-wzs-p3-dip-prewave-saiap/daily-metrics/function"
)

const (
	port = ":8080"
	// human_judged_base_path = "dip-prewave-saiap"
	ori_dateformat = "20060102"
	tar_dateformat = "2006-01-02"
	schedule_human_rejudge_to_metrics = "30 0-12 * * *"
)

var (
	FTPHOST = os.Getenv("FTPHOST")
	USER = os.Getenv("USER")
	PASSWORD = os.Getenv("PASSWORD")
	CRONDAYS = os.Getenv("CRONDAYS")
	FILESERVERURL = os.Getenv("FILESERVERURL")
	IMGEXTENSION = os.Getenv("IMGEXTENSION")
	ENVLINE = os.Getenv("ENVLINE")
	BASEPATH = os.Getenv("BASEPATH")

	// Metrics for daily rate
	// promRegistry = prometheus.NewRegistry()
	promTrueNG = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "metrics_true_ng",
			Help: "Number of both NG judged by human & AI",
		},
		[]string{"line", "date", "comp",},
	)
	promTrueOK = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "metrics_true_ok",
			Help: "Number of both OK judged by human & AI",
		},
		[]string{"line", "date", "comp",},
	)
	promFalseNG = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "metrics_false_ng",
			Help: "Overkill; Number of OK judged by human BUT NG judged by AI",
		},
		[]string{"line", "date", "comp",},
	)
	promFalseOK = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "metrics_false_ok",
			Help: "Leak; Number of NG judged by human BUT OK judged by AI",
		},
		[]string{"line", "date", "comp",},
	)
	promIPFalseOK = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "metrics_inversepolarity_leak",
			Help: "Inverse Polarity Leak; Number of NG-InversePolarity judged by human BUT OK judged by AI",
		},
		[]string{"line", "date", "comp",},
	)
	// Metrics for log
	promOverkillFN = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "filename_of_overkill",
			Help: "Filename of Overkill by date saved in label",
		},
		[]string{"filename", "line", "date", "comp", "imgurl"},
	)
	promLeakFN = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "filename_of_leak",
			Help: "Filename of Leak by date saved in label",
		},
		[]string{"filename", "line", "date", "comp", "imgurl"},
	)
	promIPLeakFN = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "filename_of_inversepolarity_leak",
			Help: "Filename of Inverse Polarity Leak by date saved in label",
		},
		[]string{"filename", "line", "date", "comp", "imgurl"},
	)
)

func init() {
	log.SetFlags(log.Ldate|log.Ltime|log.Lshortfile)
	prometheus.MustRegister(
		promTrueNG, promTrueOK, promFalseNG, promFalseOK, promIPFalseOK,
		promOverkillFN, promLeakFN, promIPLeakFN)
	fmt.Println("program init")
	human_rejudge_to_metrics("0")
}

func main() {
	fmt.Println("program main")
	c := cron.New()
	// "@every 1m"
	c.AddFunc(schedule_human_rejudge_to_metrics, func() {
		fmt.Print(time.Now().String())
		fmt.Println(" updated!")
        human_rejudge_to_metrics(CRONDAYS)
    })
	c.Start()
	// http.Handle("/metrics", promhttp.HandlerFor(promRegistry, promhttp.HandlerOpts{})) // Nothing
	http.Handle("/metrics", promhttp.Handler()) // all other default metrics from golang
	log.Fatal(http.ListenAndServe(port, nil))
}

func human_rejudge_to_metrics(days string) {
	c, err := ftp.Dial(FTPHOST, ftp.DialWithTimeout(5*time.Second))
	if err != nil {
		log.Fatalf("dial error: %v", err)
	}

	if err = c.Login(USER, PASSWORD); err != nil {
		log.Fatalf("login error: %v", err)
	}
	if ENVLINE == "LOOP_LINES" {
		lines := function.Loop_Until_Connect(c, BASEPATH)
		for _, l := range lines {
			line := l.Name
			dates := function.Loop_Until_Connect(c, path.Join(BASEPATH, line))
			for _, d := range dates {
				date := d.Name
				// last4date  := date[len(date)-4:]
				if days != "0" {
					if function.Judge_If_Date_Out_Of_Range(date, days) {
						continue
					}
				}
				fulldate := function.To_Date_Format(date)
				datepath := path.Join(BASEPATH, line, date)
				M, F := function.Request_Metrics_By_Date(c, datepath)
				// fmt.Println(f.Overkill) // filename1\ filename2\ 
				if function.Check_Daily_Metrics_If_All_Null_By_Each_Slice(M) {
					expose_metrics_by_date(M, line, fulldate)
					expose_filename_with_date_line(F, line, fulldate, date)
				}
			}
		}
	} else {
		dates := function.Loop_Until_Connect(c, BASEPATH)
		for _, d := range dates {
			date := d.Name
			// last4date  := date[len(date)-4:]
			if days != "0" {
				if function.Judge_If_Date_Out_Of_Range(date, days) {
					continue
				}
			}
			fulldate := function.To_Date_Format(date)
			datepath := path.Join(BASEPATH, date)
			M, F := function.Request_Metrics_By_Date(c, datepath)
			// fmt.Println(f.Overkill) // filename1\ filename2\ 
			if function.Check_Daily_Metrics_If_All_Null_By_Each_Slice(M) {
				expose_metrics_by_date(M, ENVLINE, fulldate)
				expose_filename_with_date_line(F, ENVLINE, fulldate, date)
			}
		}
	}
	if err = c.Quit(); err != nil {
		log.Fatalf("quit error: %v", err)
	}
}

func expose_metrics_by_date(m *function.Daily_Metrics, line string, fulldate time.Time) {
	for _, mm := range m.TrueNG {
		promTrueNG.WithLabelValues(line, fulldate.Format(tar_dateformat), mm.Component).Set(float64(mm.Amount))
	}
	for _, mm := range m.TrueOK {
		promTrueOK.WithLabelValues(line, fulldate.Format(tar_dateformat), mm.Component).Set(float64(mm.Amount))
	}
	for _, mm := range m.FalseNG {
		promFalseNG.WithLabelValues(line, fulldate.Format(tar_dateformat), mm.Component).Set(float64(mm.Amount))
	}
	for _, mm := range m.FalseOK {
		promFalseOK.WithLabelValues(line, fulldate.Format(tar_dateformat), mm.Component).Set(float64(mm.Amount))
	}
	for _, mm := range m.IPFalseOK {
		promIPFalseOK.WithLabelValues(line, fulldate.Format(tar_dateformat), mm.Component).Set(float64(mm.Amount))
	}
}

func expose_filename_with_date_line(f *function.Daily_Filenames, line string, fulldate time.Time, dirdate string) {
	for _, ff := range f.Leak {
		L_splitted := strings.Split(ff.Filename, " ")
		for _, s := range L_splitted {
			if strings.TrimRight(s, "\n") != "" {
				if ENVLINE == "LOOP_LINES" {
					imgurl := function.Concat_To_Img_Url(FILESERVERURL, line, dirdate, "Leak", s, IMGEXTENSION)
					promLeakFN.WithLabelValues(s, line, fulldate.Format(tar_dateformat), ff.Component, imgurl).Set(1)
				} else {
					imgurl := function.Concat_To_Img_Url(FILESERVERURL, "NOLINEINURL", dirdate, "Leak", s, IMGEXTENSION)
					promLeakFN.WithLabelValues(s, line, fulldate.Format(tar_dateformat), ff.Component, imgurl).Set(1)
				}
			}
		}
	}
	for _, ff := range f.Overkill {
		O_splitted := strings.Split(ff.Filename, " ")
		for _, s := range O_splitted {
			if strings.TrimRight(s, "\n") != "" {
				if ENVLINE == "LOOP_LINES" {
					imgurl := function.Concat_To_Img_Url(FILESERVERURL, line, dirdate, "Overkill", s, IMGEXTENSION)
					promOverkillFN.WithLabelValues(s, line, fulldate.Format(tar_dateformat), ff.Component, imgurl).Set(0)
				} else {
					imgurl := function.Concat_To_Img_Url(FILESERVERURL, "NOLINEINURL", dirdate, "Overkill", s, IMGEXTENSION)
					promOverkillFN.WithLabelValues(s, line, fulldate.Format(tar_dateformat), ff.Component, imgurl).Set(0)
				}
			}
		}
	}
	for _, ff := range f.IPLeak {
		IPL_splitted := strings.Split(ff.Filename, " ")
		for _, s := range IPL_splitted {
			if strings.TrimRight(s, "\n") != "" {
				if ENVLINE == "LOOP_LINES" {
					imgurl := function.Concat_To_Img_Url(FILESERVERURL, line, dirdate, "Leak/InversePolarity", s, IMGEXTENSION)
					promIPLeakFN.WithLabelValues(s, line, fulldate.Format(tar_dateformat), ff.Component, imgurl).Set(1)
				} else {
					imgurl := function.Concat_To_Img_Url(FILESERVERURL, "NOLINEINURL", dirdate, "Leak/InversePolarity", s, IMGEXTENSION)
					promIPLeakFN.WithLabelValues(s, line, fulldate.Format(tar_dateformat), ff.Component, imgurl).Set(1)
				}
			}
		}
	}
}