package function

import (
	// "fmt"
	"log"
	"path"	
	"github.com/jlaffaye/ftp"
)

const (
	ori_dateformat = "20060102"
	TN_path = "NG"
	TO_path = "OK"
	FN_path = "Overkill"
	FO_path = "Leak"
	IP_path = "InversePolarity"
	attempt_max = 30
)

type Metrics struct{
	Component string
	Amount    int
}

type MetricsSlice []Metrics

type Daily_Metrics struct{
	TrueNG  MetricsSlice
	TrueOK  MetricsSlice
	FalseNG MetricsSlice
	FalseOK MetricsSlice
	IPFalseOK MetricsSlice
}

type Filenames struct{
	Component string
	Filename string
}

type Daily_Filenames struct{
	Overkill []Filenames
	Leak     []Filenames 
	IPLeak     []Filenames 
}

func Request_Metrics_By_Date(c *ftp.ServerConn, datepath string) (*Daily_Metrics, *Daily_Filenames) {
	M := Daily_Metrics{}
	M.TrueNG  = count_files_walking_folder_path(c, path.Join(datepath, TN_path))
	M.TrueOK  = count_files_walking_folder_path(c, path.Join(datepath, TO_path))
	M.FalseNG = count_files_walking_folder_path(c, path.Join(datepath, FN_path))
	M.FalseOK = count_files_walking_folder_path(c, path.Join(datepath, FO_path))
	M.IPFalseOK = count_files_walking_folder_path(c, path.Join(datepath, FO_path, IP_path))
	F := Daily_Filenames{}
	F.Overkill= append_filenames_walking_folder_path(c, path.Join(datepath, FN_path))
	F.Leak    = append_filenames_walking_folder_path(c, path.Join(datepath, FO_path))
	F.IPLeak    = append_filenames_walking_folder_path(c, path.Join(datepath, FO_path, IP_path))
	return &M, &F
}

func count_files_walking_folder_path(c *ftp.ServerConn, filepath string) MetricsSlice{
	attempt_conn := 0
	for attempt_conn < attempt_max {
		var UnderPathML MetricsSlice
		files, err := c.List(filepath)
		if err != nil {
			attempt_conn++
		} else {
			comps := comp_under_dir(files)
			if comps == nil {
				return UnderPathML
			} else {
				amounts := amount_under_dir(files, comps)
				for index, comp := range comps {
					UnderPathML = append(UnderPathML, Metrics{Component: comp, Amount: amounts[index]})
				}
			}
		}
		return UnderPathML
	}
	log.Println(filepath, " does not exist, return count equal to 0")
	var UnderPathML MetricsSlice
	return UnderPathML
}

func append_filenames_walking_folder_path(c *ftp.ServerConn, filepath string) []Filenames{
	attempt_conn := 0
	for attempt_conn < attempt_max {
		var UnderPathFilenames []Filenames
		files, err := c.List(filepath)
		if err != nil {
			attempt_conn++
		} else {
			comps := comp_under_dir(files)
			if comps == nil {
				return UnderPathFilenames
			} else {
				fns := filenames_by_comps(files, comps)
				for index, comp := range comps {
					UnderPathFilenames = append(UnderPathFilenames, Filenames{Component: comp, Filename: fns[index]})
				}
			}
		}
		return UnderPathFilenames
	}
	log.Println(filepath, " does not exist, return empty string")
	var UnderPathFilenames []Filenames
	return UnderPathFilenames
}