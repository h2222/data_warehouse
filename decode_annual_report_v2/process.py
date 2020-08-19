#coidng=utf-8
import os, sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decode_annual_report.annual_utils import punctuation, position_set, company_entity, all_names, all_entity


def zero_size_file_num(folder_path, end):
    files = os.listdir(folder_path)
    for f in files[:end]:
        file_size = os.path.getsize(os.path.join(folder_path, f))
        if file_size == 0:
            f_num = re.split('_|\.', f)[1]
            yield f_num+'.txt'


def get_failed_file_path(folder_path, input_path, save_list, date=20100101):
    cc = 0
    valid_f = 0
    save_result = []
    for i in zero_size_file_num(folder_path, -1):
        cc += 1
        in_fpath = os.path.join(input_path, i)
        # print(in_fpath)
        try:
            f = open(in_fpath, 'r')
        except:
            continue
        if os.path.exists(save_list):
            os.remove(save_list)
            open(save_list, 'w')
        else:
            open(save_list, 'w')
        c = 0
        for line in f.readlines():
            if "FILED AS OF DATE" in line:
                ll = re.split("\t|\n|\\ ", line)
                data = 0
                for i in ll:
                    try:
                        data = int(i)
                    except:
                        continue
                if data > date:
                    valid_f += 1
                    save_result.append(in_fpath+'\n')
                    f.close()
                    break
            c += 1
            if c > 80: # max check line
                break           
    sf = open(save_list, 'a')
    sf.writelines(save_result)
    print("total:{}, valid:{}".format(cc, valid_f))

def process(path):
    f = open(path, 'r')
    path_save = './test_split.txt'
    patient = 0
    sp_token = "FILER"
    sp_pass = False
    no_stop = False
    f2 = open(path_save, 'w')
    for o in f.readlines():
        i = o.lstrip()

        i2 = i.replace('\n', '')
        i3 = i2.split(" ")
        # i3 = re.split("\s|", i2)
        # print(i3)
        with open(path_save, 'a') as f2:
            if len(i3) == 1 and i3[0] == '':
                if no_stop:
                    f2.write('\n')
                    no_stop = False
                else:
                    f2.write('***'*20+'\n')
                continue
            elif i3.count('') > 0.33 * len(i3):
                if patient == 0:
                    patient = 20
                no_stop = True
                f2.write(o) 
                continue
        
            if patient != 0:
                # temp = o.split(' ')
                # if temp.count('') > 0.33 * len(temp):
                f2.write(o)
                patient -= 1
    


if __name__ == "__main__":
    path1 = "/data/lichang/cik_def_14a_v2"
    in_path1 = "/data/download_data/cik_def_14a"
    save_to1 = "14k.txt"
    
    path2 = "/data/lichang/cik_10_k_v2"
    in_path2 = "/data/download_data/cik_10_k/output"
    save_to2 = "10k.txt"
    
    path3 = "/data/lichang/cik_20_f_v2"
    in_path3 = "/data/download_data/cik_20_k/output"
    save_to3 = "20k.txt"

    print(in_path1)
    get_failed_file_path(path1, in_path1, save_to1)
    print(in_path2)
    get_failed_file_path(path2, in_path2, save_to2)
    print(in_path3)
    get_failed_file_path(path3, in_path3, save_to3)
 
    # p1 = '/data/download_data/cik_10_k/output/935493.txt'
    # p2 = '/data/download_data/cik_def_14a/1383496.txt'
    # process(p2)
    