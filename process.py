# -*- coding: utf-8 -*-
import os, sys
import re
from nltk.tokenize import word_tokenize
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decode_annual_report.annual_utils import punctuation, position_set, company_entity, all_names, all_entity


def get_failed_file_path(folder_path, input_path, save_list, date=20100101):
    cc = 0
    valid_f = 0
    save_result = []
    for file in os.listdir(folder_path):
        if os.path.getsize(os.path.join(folder_path, file)) > 0:
            continue
        cc += 1
        file_name = file.split("_")[-1]
        input_file_path = os.path.join(input_path, file_name)
        if not os.path.exists(input_file_path):
            continue
        date_line = os.popen('cat %s |grep "FILED AS OF DATE"' % input_file_path).read()
        ll = [x for x in re.split("\t|\n|\\ ", date_line) if x.strip().isdigit()]
        if len(ll) == 0:
            continue
        line_date_res = int(ll[-1])
        if date >= line_date_res:
            continue
        valid_f += 1
        save_result.append(input_file_path + "\n")
    sf = open(save_list, 'w')
    sf.writelines(save_result)
    print("total:{}, valid:{}".format(cc, valid_f))
    return save_result


def get_table(path, save_path, print_all=False):
    ## create dir
    duc = re.split("\/|\.", path)[-2]
    save_path = os.path.join(save_path, duc)
    for tp in ['name', 'company', 'position']:
        tp_dir = os.path.join(save_path, tp)
        if not os.path.isdir(tp_dir):
            print(tp_dir)
            os.system('mkdir -p %s' % tp_dir)
        else:
            print(tp_dir)
            os.system('rm -r %s' % tp_dir)
            os.system('mkdir -p %s' % tp_dir)
    ## detect
    f = os.popen('cat %s' % path).readlines()
    patient = 0
    dont_stop = 0
    f2 = []
    for i1 in f:
        i2 = i1.lstrip().replace('\n', '')
        i3 = i2.split(" ")
        # condition1: the "''" number is 33% of the total elements in a line.
        cond1 = i3.count('') > 0.33 * len(i3)
        # condition2:
        # condition3:
        # ...  
        if len(i3) == 1 and i3[0] == '': # None line
            if dont_stop != 0:
                f2.append('\n')
                dont_stop -= 1
            else:
                f2.append('^^^'+'\n')
            continue
        elif cond1:
            if patient == 0:
                patient = 10
            if dont_stop == 0:
                dont_stop = 6
            f2.append(i1) 
            continue
        if patient != 0:
            f2.append(i1)
            patient -= 1

    if print_all:
        mp1 = os.path.join(save_path, 'middle_result_1.txt')
        m1 = open(mp1, 'w')
        m1.writelines(f2)  

    ## filter
    f3 = []
    table = False
    start = True
    table_c = 0
    ccc = 0
    for i in range(0, len(f2)-5):
        jump = False
        if "^" in f2[i]:
            if table: # end table line
                f2[i] = "###" * 55 + '\n'
                f3.append(f2[i])
                start = True
                table = False
            jump = True
        for j in range(i, i+5): # check next 5 items
            if "^" in f2[j] and not table:
                jump = True
        if jump:
            ccc += 1
            continue
        if start: # find table line 
            table_c += 1
            start = False
        f3.append(f2[i])
        table = True

    if print_all:
        mp2 = os.path.join(save_path, 'middle_result_2.txt')
        m2 = open(mp1, 'w')
        m2.writelines(f3)  
    
    print("table count: ", str(table_c))
    ## split
    f3len = len(f3)
    first = True
    set_total = set()
    start_idx = 0
    end_idx = 0
    name_c = 0
    company_c = 0
    position_c = 0
    for i in range(1, f3len):
        if f3[i-1].count("#") > 10:
            if first:
                start_idx = i
                first = False
            line_set = set(word_tokenize(f3[i]))
            line_set = word_tokenize(f3[i])
            line_set = set(list(map(lambda x : x.lower(), line_set))) # to lower case
            set_total |= line_set
        if f3[i].count("#") > 10 and f3[i-1].count("#") < 10:
            end_idx = i
            company_num = len(set_total & company_entity)
            name_num = len(set_total & all_names)
            position_num = len(set_total & position_set)
            table_type_d = {"company":company_num, "name":name_num, "position":position_num}
            c = 0
            table_type = ""
            for k in table_type_d:
                if c < table_type_d[k]:
                    table_type = k 
            # print('range:{}-{}, company_num:{}, name_num:{}, position_num:{}'.format(start_idx, end_idx, company_num, name_num, position_num))
            if table_type == "company":
                company_c += 1
                cpath = os.path.join(save_path, 'company')
                cpath = os.path.join(cpath, duc + '_company_' + str(company_c) + '.txt')
                f = open(cpath, 'w')
                f.writelines(f3[start_idx:end_idx]) 
            elif table_type == "name":
                name_c += 1
                npath = os.path.join(save_path, 'name')
                npath = os.path.join(npath, duc + '_name_' + str(name_c) + '.txt')
                f = open(npath, 'w')
                f.writelines(f3[start_idx:end_idx])
            elif table_type == "position":
                position_c += 1
                ppath = os.path.join(save_path, 'position')
                ppath = os.path.join(ppath, duc + '_position_' + str(position_c) + '.txt')
                f = open(ppath, 'w')
                f.writelines(f3[start_idx:end_idx+1])
            # reset
            set_total = set()       
            first = True

if __name__ == "__main__":
    check_date = 20100101
    path1 = "/data/lichang/cik_def_14a_v2"
    in_path1 = "/data/download_data/cik_def_14a"
    save_to1 = "14k-%d.txt" % check_date
    path2 = "/data/lichang/cik_10_k_v2"
    in_path2 = "/data/download_data/cik_10_k/output"
    save_to2 = "10k-%d.txt" % check_date
    path3 = "/data/lichang/cik_20_f_v2"
    in_path3 = "/data/download_data/cik_20_k/output"
    save_to3 = "20k-%d.txt" % check_date
    
    
    
    path4 = '/data/lichang/cik_def_14a_v2_blank'
    in_path4 = "/data/download_data/cik_def_14a"
    save_to4 = "14k-%d.txt" % check_date
    print(in_path4)
    save_result = get_failed_file_path(path4, in_path4, save_to4, check_date)
#    print(in_path1)
#    get_failed_file_path(path1, in_path1, save_to1, check_date)
#    print(in_path2)
#    get_failed_file_path(path2, in_path2, save_to2, check_date)
#    print(in_path3)
#    get_failed_file_path(path3, in_path3, save_to3, check_date)
#
    path = '/data/download_data/cik_def_14a'
    save_to = './result_test'
    #for file in os.listdir(path):
    #    file_name = file.split("/")[-1]
    #    ff = os.path.join(path, file_name)
    #    if not os.path.exists(ff):
    #        print("file not exist")
    #        continue
    #    print(ff)
    #    get_table(ff, save_to)
    
    #for ff in save_result:
    #    print(ff)
    #    get_table(ff, save_to)
    get_table('/data/download_data/cik_def_14a/100307.txt', save_to, print_all=True)
