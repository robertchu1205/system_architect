package function

import (
	// "fmt"

	"time"
	"reflect"
	"bytes"
	"strconv"
	"strings"
	"github.com/jlaffaye/ftp"
)

var (
	possible_comps = []string {"AluCap", "ElecCap", "acpi", "Ins", "SATA", "L", "BH", "Jumper", "PCI", "Aud", "Stud", "NI", "DimSoc", "CONN", "USB", "VGA"}
)

func Check_Daily_Metrics_If_All_Null_By_Each_Slice(m *Daily_Metrics) bool {
	MS := []MetricsSlice{m.TrueNG, m.TrueOK, m.FalseNG, m.FalseOK, m.IPFalseOK}
	for _, MM := range MS {
		for _, m := range MM {
			if m.Amount > 0 {
				return true
			}
		}
	}
	return false
}

func Check_Daily_Metrics_If_All_Null(m *Daily_Metrics) bool {
	values := reflect.ValueOf(*m)
	fields := reflect.TypeOf(*m)
	num := fields.NumField()
	for i := 0; i < num; i++ {
		// field := fields.Field(i)
		value := values.Field(i)
		// fmt.Print("Type:", field.Type, ",", field.Name, "=", value, "\n")
		// for _, v := range value {
		// 	if v.amount > 0 {
		// 		return true
		// 	}
		// }
		if value.Int() > 0 {
			return true
		}
	}
	return false
}

func Check_Metrics_If_All_Null(m *Metrics) bool {
	values := reflect.ValueOf(*m)
	fields := reflect.TypeOf(*m)
	num := fields.NumField()
	for i := 0; i < num; i++ {
		// field := fields.Field(i)
		value := values.Field(i)
		if value.Int() > 0 {
			return true
		}
	}
	return false
}

func To_Date_Format(date string) time.Time{
	// year, _, _ := ftpdateinfo.Time.Date()
	// fulldate := strconv.Itoa(year) + date
	t, _ := time.Parse(ori_dateformat, date)
	return t
}

func Judge_If_Date_Out_Of_Range(date string, days string) bool {
	int_crondays, _ := strconv.Atoi(days) // string to int
	previous_date, _ := strconv.Atoi(time.Now().AddDate(0, 0, (-1 * int_crondays)).Format(ori_dateformat)) // 20200806
	date_now, _ := strconv.Atoi(time.Now().Format(ori_dateformat))
	// year, _, _ := ftpdateinfo.Time.Date()
	// dateinftp, _ := strconv.Atoi(strconv.Itoa(year) + date)
	dateinftp, _ := strconv.Atoi(date)
	if ((dateinftp > date_now) || (dateinftp < previous_date)) {
		return true
	} else {
		// fmt.Println(previous_date, date_now, dateinftp)
		return false
	}
	return false
}

func Loop_Until_Connect(c *ftp.ServerConn, path string) []*ftp.Entry{
	for {
		target, err := c.List(path)
		if err != nil{
			// log.Println(err)
		} else {
			// fmt.Println(err)
			return target
		}
	}
}

// Metrics
func parse_comp_from_fn(filename string) string{
	comp := ""
	filename_splitted := strings.Split(filename, "_")
	for _, pc := range possible_comps {
		for _, fs := range filename_splitted{
			if pc == fs {
				comp = fs
				break
			}
		}
	}
	return comp
}

func stringInSlice(a string, list []string) bool {
    for _, b := range list {
        if b == a {
            return true
        }
    }
    return false
}

func comp_under_dir(files []*ftp.Entry) []string{
	var comps []string
	for _, f := range files {
		if f.Type != ftp.EntryTypeFile{
			continue
		}
		parsed_comp := parse_comp_from_fn(f.Name)
		if stringInSlice(parsed_comp, comps) == false {
			comps = append(comps, parsed_comp)
		}
	}
	return comps
}

func amount_under_dir(files []*ftp.Entry, comps []string) []int{
	var amounts = make([]int, len(comps), len(comps))
	for _, f := range files {
		if f.Type != ftp.EntryTypeFile{
			continue
		}
		parsed_comp := parse_comp_from_fn(f.Name)
		for i, comp := range comps {
			if parsed_comp == comp {
				amounts[i]++
			}
		}
	}
	return amounts
}

// Overkill & Leak Filenames
func filenames_by_comps(files []*ftp.Entry, comps []string) []string{
	var fns = make([]string, len(comps), len(comps))
	for _, f := range files {
		if f.Type != ftp.EntryTypeFile{
			continue
		}
		parsed_comp := parse_comp_from_fn(f.Name)
		for i, comp := range comps {
			if parsed_comp == comp {
				fns[i] = ori_filename_append_space(fns[i], check_filenames_underlines(f.Name))
			}
		}
	}
	return fns
}

func ori_filename_append_space(ori_fn string, new_fn string) string{
	var buffer bytes.Buffer
	buffer.WriteString(ori_fn)
	buffer.WriteString(new_fn)
	buffer.WriteString(" ")
	return buffer.String()
}

func check_filenames_underlines(filename string) string{
	count := 0
	filename_splitted := strings.Split(filename, "_")
	for _, s := range filename_splitted {
		count++
		if strings.TrimRight(s, "\n") == "" {
			break
		}
	}
	var buffer bytes.Buffer
	combine := 0
	if count == 11 {
		for _, s := range filename_splitted {
			combine++
			if combine != count {
				if combine == count-1 {
					buffer.WriteString(s + "")
				} else {
					buffer.WriteString(s + "_")
				}
			}
			if strings.TrimRight(s, "\n") == "" {
				break
			}
		}
	} else {
		filename_dotted := strings.Split(filename, ".")
		for _, s := range filename_dotted {
			return s
		}
	}
	return buffer.String()
}

func Concat_To_Img_Url (fsurl string, line string, dirdate string, defecttype string, s string, extension string) string{
	// <a href='http://{fsurl}/{line}/{dirdate}/{defecttype}/{s}.{extension}' target='_blank'><img src='http://{fsurl}/{line}/{dirdate}/{defecttype}/{s}.{extension}'>
	var buffer bytes.Buffer
	buffer.WriteString("<a href='http://")
	buffer.WriteString(fsurl)
	buffer.WriteString("/")
	if line != "NOLINEINURL" {
		buffer.WriteString(line)
		buffer.WriteString("/")
	}
	buffer.WriteString(dirdate)
	buffer.WriteString("/")
	buffer.WriteString(defecttype)
	buffer.WriteString("/")
	buffer.WriteString(s)
	buffer.WriteString(".")
	buffer.WriteString(extension)
	buffer.WriteString("' target='_blank'><img src='http://")
	buffer.WriteString(fsurl)
	buffer.WriteString("/")
	if line != "NOLINEINURL" {
		buffer.WriteString(line)
		buffer.WriteString("/")
	}
	buffer.WriteString(dirdate)
	buffer.WriteString("/")
	buffer.WriteString(defecttype)
	buffer.WriteString("/")
	buffer.WriteString(s)
	buffer.WriteString(".")
	buffer.WriteString(extension)
	buffer.WriteString("'>")
	return buffer.String()
}