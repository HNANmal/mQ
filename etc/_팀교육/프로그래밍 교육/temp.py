# Load the Python Standard and DesignScript Libraries
import sys
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

#################################Module For Functional Programing#############################################
from functools import reduce
from itertools import chain
from itertools import groupby
from copy import deepcopy
curry = lambda f: lambda a,*args: f(a, *args) if (len(args)) else lambda *args: f(a, *args)

filter = curry(filter)
map = curry(map)
reduce = curry(reduce)

go = lambda *args: reduce(lambda a,f: f(a), args) ## �Լ��� ��� ���� ##

def dictUpdate(dic1,dic2):
    res = dic1.update(dic2)
    #res = {**dic1,**dic2}
    return dic1 #res
    
def dictsMerge(dics):
    res = reduce(dictUpdate, dics)
    return res
    
def dictDeleteKeys(dic, keys):
    for k in keys:
        del dic[k]
    return dic
##############################################################################################################

import re
from functools import partial

# The inputs to this node will be stored as a list in the IN variables.
dataEnteringNode = IN
lang_mode = IN[0]
wholeDatas = IN[1]
db = wholeDatas[1:]
allCatSheetsNames = IN[2][2:]

calcStdSheet = db[0] ##������� ��Ʈ
allCatSheets = db[1:]


# Place your code below this line

def find_IsInStr(target, string):
    if target == None or string == None:
        pass
    else:
        res = str(target) in str(string)
        return res

def find_range_by_columnItem(db, col_idx, sep_rule):
    tdb = list(map(lambda x: x[col_idx], db)) ##targetTransposedDB (col_idx�� �ش��ϴ� �����͸� ����)
    last_idx_tdb = len(tdb)-1
    tdb_enum = enumerate(tdb)
    target_RowNumber = list(filter(lambda x: find_IsInStr(sep_rule, x[1]), tdb_enum))
    endidxs_tmp= list(map(lambda x: x[0]-1,target_RowNumber))
    endidxs_tmp.pop(0)
    endidxs = endidxs_tmp + [last_idx_tdb] ## �� ������ ������ �� ��ȣ
    rangeSttIdxs = list(map(lambda x: x[0]+1,target_RowNumber))
    rangeEndIdxs = endidxs
    result = list(zip(rangeSttIdxs, rangeEndIdxs))
    return result

    
def find_headersAtSheet(sheet):
    headers_sheet = map(lambda x: [x[1].replace("\n",""),x[0]], filter(lambda x: x[1] != None, enumerate(sheet[1])))
    
    #return dict(headers_sheet)
    return list(headers_sheet)

def find_rangesAtSheet(sheet, hdrs_withIdx, trgt_hdr, trgt_str):
    hdrs_withIdxDict = dict(hdrs_withIdx)
    return find_range_by_columnItem(sheet, hdrs_withIdxDict[trgt_hdr], trgt_str)


def get_DataOnRowAreasAtSheet(sheet:list, discrHDRStr, discrRowStr):
    """
    �Ǻ����� Header���ڿ�(discrHDRStr)�� ����ִ� ������,
    �Ǻ����� �� ���ڿ�(discrRowStr)�� ����ִ� ���ȣ �������� ������ ������ ������ ����Ʈ ��ȯ
    """
    
    hdrs_withIdx = find_headersAtSheet(sheet)
    rowAreasAtSheet = find_rangesAtSheet(sheet, hdrs_withIdx, discrHDRStr, discrRowStr)
    typesTitle_idx = list(map(lambda x: x[0]-1, rowAreasAtSheet)) # �� Ÿ�� ���� ��ġ�� �ε���
    rowsGrps_perType_withNone = list(map(lambda x: sheet[x[0]-1:x[1]], rowAreasAtSheet))
    # None����
    rowsGrps_perType = go(
        rowsGrps_perType_withNone,
        ## �ϳ��� Ÿ���� �����ϴ� ����� ���ӿ���
        map(lambda rowGrp: \
        ## �� �྿ ���
        map(lambda row: \
        ## ���� �����ϴ� �� �� �� None�� ������ ���ڿ��� ġȯ
        map(lambda cell: "" if cell==None else cell, row), rowGrp) ),
        ## �� ��ü�� ��ȯ�ǹǷ� ����Ʈ ��ȯ
        list,
    )
    
    return (rowsGrps_perType, hdrs_withIdx)


def setDict_OnEachCalType(data_perType, hdrs_withIdx):
    """
    data_perType: '#' ���� ���б�ȣ�� ���� �������� �� ���� �� ��ü ������_(��������� ���е� ����)
    """
    hdrs_withIdxDict = dict(hdrs_withIdx)
    eff_hdrs_idx = list(zip(*hdrs_withIdx))[1]
    eff_hdrs_name = list(zip(*hdrs_withIdx))[0]
    # 
    calcTypeName = data_perType[0][hdrs_withIdxDict["Q'ty Cal Type Tag"]]

    paramDicts_withTypeName = go(
        data_perType,
        ## ���� "�׸�" ���� ���� ���� �� ����
        filter(lambda row: row[hdrs_withIdxDict["�׸�"]] != None), list,
        
        ## ��� Null �� ���ڿ��� ġȯ
        map(lambda row: list(map(lambda cell: cell if cell!=None else "",row))), list,

        ## ����� �ش��ϴ� �� ���� ����--
        map(lambda row: list(map(lambda idx: row[idx], eff_hdrs_idx))), list,
        
        ## ����̸��� �� ������ ���� 2���� ¦���� ��
        map(lambda row: list(zip(eff_hdrs_name, row))), list,
        
        ## ����̸� : ���� ���·� �� �� �����͸� ��ųʸ��� ����
        map(lambda x: dict(x)), list,
        
        ## "������� ����" Ű�� �Ҵ�� ���� ���ڿ��� ��� ����
        filter(lambda d: d["������� ����"]!=""), list,
        
        ## ��ųʸ��� "Q'ty Cal Type Tag" Ű-�� �߰�
        map(lambda d: dictUpdate(d,{"Q'ty Cal Type Tag":calcTypeName})), list,
        
        ## ��ųʸ��� "applyForCalc" Ű-�� �߰�
        ## ("���� �Է°�"�׸��� �ִ� ��쿡�� �װ��� �����ϰ� �ƴѰ�� "Parameter"�׸� ��
        map(lambda d: dictUpdate(d, { "applyForCalc":\
            d["���� �Է°�"] if d["���� �Է°�"] != "" \
            else d["Parameter"] if d["Parameter"] != "" \
            else 0 })), list,
        
        ## Ÿ���̸��� Ű������ �ϴ� ��ø ��ųʸ� ����
        lambda x: {calcTypeName: x},
    )

    return paramDicts_withTypeName

###################################################################################################################
#!!! �Լ��� �ʹ� ũ�� �ɰ���
#!!! setDict_OnEachFamType
#!!! -> setDict_EachRow_perGroup//setDict_stdWM_perGroup//setDict_applied_perGroup
###################################################################################################################

#def setDict_OnEachFamType(data_perType, hdrs_withIdx, cat=None):


def setDict_OnEachFamType(data_perType, hdrs_withIdx, cat=None):
    """
    data_perType: '#' ���� ���б�ȣ�� ���� �������� �� ���� �� ��ü ������_(��������� ���е� ����)
    hdrs_withIdx: ��� ��� �ε��� ��ȣ�� ������� ������ ��ø ����Ʈ
    cat : Room ��Ʈ ���� �Ǻ��� �Է°�
    """
    hdrs_withIdxDict = dict(hdrs_withIdx)
    eff_hdrs_idx = list(zip(*hdrs_withIdx))[1]
    eff_hdrs_name = list(zip(*hdrs_withIdx))[0]
    # data_perType ����, Ÿ�� �׷� ���� "Q'ty Cal Type Tag" ���� �ִ� ����
    # None�϶��� �����Ƿ� ����ó���� ���ִ� ����
    calcTypeName = data_perType[0][hdrs_withIdxDict["Q'ty Cal Type Tag"]] \
        if data_perType[0][hdrs_withIdxDict["Q'ty Cal Type Tag"]]!=None else "N/A"
    stdFamTypeNo = data_perType[0][hdrs_withIdxDict["NO"]]
    stdFamTypeName = data_perType[0][hdrs_withIdxDict["Standard Type"]]

    wmspec_headers = ["Work Master Code", "GaugeCode", "Unit"]\
        + list(filter(lambda x: "Work Cat" in x or "Spec" in x, eff_hdrs_name))\
        + ["Description","����_���������", "����_���������"]
    
    # �׷� ���� ��� ���� ����Ʈ���� Į�� ���� ���� ��ųʸ��� ��ȯ�ϴ� ����
    # ���� ���� �йи� Ÿ�� �� ���� �����Ҵ� WM ����
    rowDicts = go(
        data_perType,
        ## ��� Null �� ���ڿ��� ġȯ
        map(lambda row: list(map(lambda cell: cell if cell!=None else "",row))), list,
        
        ## ����� �ش��ϴ� �� ������ ����
        map(lambda row: list(map(lambda idx: row[idx], eff_hdrs_idx))), list,
        
        ## ����̸��� �� ������ ���� 2���� ¦���� ��
        map(lambda row: list(zip(eff_hdrs_name, row))), list,        

        ## ����̸� : ���� ���·� �� �� �����͸� ��ųʸ��� ����
        map(lambda x: dict(x)), list,
    )

    # �׷� ���� ��� ���ųʸ� �� �� ã���� �ϴ� ��Ģ�� ���� ������ ���θ� ��ȯ�ϴ� ��
    def findRow_AppliedType(rowDict, tgtHDRname, rule=None):
        p = re.compile('[0-9]{3,5}')
        target = str(rowDict[tgtHDRname])
        ## �Լ� ȣ��� ������(rule) ���� ȣ���� ���
        ## -Room Category ��Ʈ �� �̸� "Standard Type" �׸��� ���� 000������ ���������� �Ǻ�
        ## -Room Category �� "Standard Type" Į���� �� �ѹ�, "Family Type Name" Į���� �� �̸� �Է��ϰ� �Ǿ�����
        if rule==None:
            p = re.compile('[0-9]{3,5}')
            m = p.match(target)
            stdCase = target =="Room No"
            res = all([m or stdCase])
        ## ������(rule)�� ����ǥ���� ��ü�� ���� ���
        elif isinstance(rule, re.Pattern):
            m = p.match(target)
            res = all([m])
        ## ������(rule)�� ���ڿ��� ���� ���
        else:
            res = rule in target
        return res
    
    # �׷� ���� ��� �� ��ųʸ� ��, ���� ���� �йи����� �ƴ� ���� WM �׸� ���� ���� ����
    stdFamTypeInfo = go(
        rowDicts,
        ## ���� "���������", "Work Master Code" ���� ���� ���� �� ����
        ## Family Type Name�� "H_" ���ڿ� ���Ե� ��� ����
        filter(lambda d: d["����_���������"] != ""),
        filter(lambda d: d["����_���������"] != ""),
        filter(lambda d: d["Work Master Code"] != ""),
        filter( lambda d: \
            (not findRow_AppliedType(d, "Standard Type")) or (not findRow_AppliedType(d, "Standard Type", rule="H_")) \
            ### ��ī�װ��� ���� "Standard Type"�׸� ���� ���ڰ� �ƴϰų�, "H_"���ڿ��� ���Ե��� ���� �׸� ����
            if cat == "roomCat" else\
            ### ��ī�װ��� �ƴ� ���, "Family Type Name" �׸� "H_"���ڿ� ���Ե��� ���� �׸� ���� 
            not findRow_AppliedType(d, "Family Type Name", rule="H_") ),
        list,
        
        # wmSpecs �Ӽ����� ����� �ϴ� ���ο� ��ųʸ� ���� �� �� �߰�(���� list����)
        map( lambda d: \
            go(
                ### wmspec���� �׸�� ���� ����Ʈ�� ����
                map(lambda x: d[x], wmspec_headers), list,
                ### �׸��� �׸��� ��Ƽ� ��ųʸ� ���·� ��ȯ
                lambda x: zip(wmspec_headers,x), dict,
            )
        ),
        list,
    )
    
    def dictsUnion_withInnerKey(dicts:list,innerkey):
        """
        �ֻ��� Ű���� "�ϳ�"�̰�, �� ������ ���ӵ� ��ųʸ��� Ű������ ������ ������ ��ųʸ� �� ,
        Ű ���� ������ ���� ���� �� ��ųʸ����� �ش� Ű�� �����ϴ� ������
        �� ó���� ��ųʸ��� ������ ���Ҵ��ϰ� �ش� ��ųʸ��� ��ȯ
        """
        # �ֻ��� Ű���� �������� ��ųʸ��� �׷���
        if len(dicts) != 0:
            groupedDicts = go(
                dicts,
                lambda col: sorted(col, key=lambda x:list(x.keys())),
                lambda col: groupby(col, lambda x: list(x.keys())),
                map(lambda x: list(map(lambda y: list(y), x))),
                list,
            )
            # �ֻ��� Ű���� �ߺ��Ǵ� ��ųʸ��� ���� ����Ʈ
            plurals = list(map(lambda y: y[1], filter(lambda x: len(x[1])>1, groupedDicts)))
            # �ֻ��� Ű���� �ٸ� � ��ųʸ��� �ߺ����� �ʴ� ���� ��ü�� ���� ����Ʈ
            singles = list(map(lambda y: y[1][0], filter(lambda x: len(x[1])==1, groupedDicts)))
            # �Ϻε�ųʸ� ����Ű ��ü
            #hdrs = list(dicts[0][list(dicts[0].keys())[0]].keys())
            
            # plurals ���� ��� ó��
            if len(plurals)==0:
                res = singles
            else:
                newPlurals = []
                for sameKeyGroup in plurals:
                    ### �ֻ�� Ű
                    titleKey = list(sameKeyGroup[0].keys())[0]
                    newD = deepcopy(sameKeyGroup[0])
                    newD[titleKey][innerkey]=[]
                    for d in sameKeyGroup:
                        newD[titleKey][innerkey].append(d[titleKey][innerkey][0])
                    newPlurals.append(newD)
                res = newPlurals + singles
        
            return res
        
    # �׷� ���� ��� �� ��ųʸ� ��, ���� ���� �йи��� ���� ���� ����
    # ���� ��Ʈ���� "Family Type Name" Į���� ���� ��������� ���Ե� ��� �� ���
    actualAppliedFamTypeInfo = go( ##!!! ���� �йи� �̸� �����Ѱ� ������ ���� ��ġ�� ���� �߰� �ʿ�
        rowDicts,
        ## Family Type Name �׸� �� "H_" ���ڿ��� ���Ե� ��ü�� ���͸�
        filter( lambda d: \
            findRow_AppliedType(d, "Standard Type") \
            if cat == "roomCat" else\
            findRow_AppliedType(d, "Family Type Name", rule="H_")
            ),
        
        ## �� ��ųʸ��� wmSpecs �Ӽ� �� �� �߰�(���� list����)
        ##!!! ���� �йи� �̸� �����Ѱ� ������ ���� ��ġ�� ���� �߰� �ʿ� - ���� WM �߰� �ڵ�� �и� �ʿ�
        map( lambda d: dictUpdate(d, {"wmSpecs": \
            go(
                ### wmspec���� �׸�� ���� ����Ʈ�� ����
                map(lambda x: d[x], wmspec_headers), list,
                ### �׸��� �׸��� ��Ƽ� ��ųʸ� ���·� ��ȯ
                lambda x: zip(wmspec_headers,x), dict,
                
                ### wmSpecs �׸��� ����Ʈ ������ ������ �α� & ���� WM������ ���� ���� ����Ʈ���� ����
                #lambda x: [x] if x["Work Master Code"]!="" else [],
                ### stdFamType�� WM������ ��ġ�� - ������ �и� �ʿ�
                lambda x: [ *stdFamTypeInfo, x \
                    if x["Work Master Code"]!="" else ["No Individual WM information"] ],
                ### ���� WM������ ���� ���� ����Ʈ���� ����
                filter(lambda x: isinstance(x,dict)), list,
            ) }) 
        ), list,
        
        ## ������ ������ WorkMaster ���� �Ӽ� ����
        map(lambda d: dictDeleteKeys(d, wmspec_headers)), list,
        
        ## ��ųʸ��� Q'ty Cal Type Tag Ű�� �� ������Ʈ
        map(lambda d: dictUpdate(d,{"Q'ty Cal Type Tag": calcTypeName})), list,
        
        ## ��ųʸ��� Standard TypeŰ�� �� ������Ʈ
        map( lambda d: dictUpdate(d,{"NO":d["Standard Type"], "Standard Type":stdFamTypeName})) \
            if cat=="roomCat" \
            else map(lambda d: dictUpdate(d,{"NO":stdFamTypeNo, "Standard Type":stdFamTypeName}) ), 
        list,
        
        ## ��ųʸ��� wmSpecs �� "Work Master Code" ���� GaugeCode ������ ������ ������Ʈ (�ʿ��Ѱ�?)
        
        
        ## Family Type Name ���ڿ��� Ű������ �ϴ� ��ųʸ��� ����
        #map(lambda d: {d["Family Type Name"]:d}), list,
        map(lambda d: {f'{d["NO"]}'+"_"+d["Family Type Name"]:d})\
            if cat=="roomCat" \
            else map(lambda d: {d["Family Type Name"]:d}), list,
        
        ## �ֻ��� Ű�� 1���� ��ųʸ��� �� �ֻ��� Ű ���� ���� ��ųʸ� �鸸 "wmSpecs" ���� ��ġ��
        #lambda x: dictsUnion_withInnerKey(x, "wmSpecs"),
        
    )
    
    return eff_hdrs_idx#actualAppliedFamTypeInfo



def dataToDict(setDict_f, args, cat=None):
    (datas_perType, hdrs_withIdx) = args
    res = go(
        datas_perType,
        ## 
        map( lambda datas: \
            setDict_f(datas, hdrs_withIdx, cat=cat) if cat=="roomCat" \
            else setDict_f(datas, hdrs_withIdx)
        ),
            
        ## �� ����Ʈ�� ��ġ�� �� ���� ��ü ����
        filter(lambda x: x!=[] and x!=None), list,
        
        ## ������� ��Ʈ��, ī�װ��� ��Ʈ�� ���� ������� ����� ���� �ٸ��Ƿ�
        ## �� ���� �����Ͱ� ����Ʈ���� ���θ� Ȯ���� �����ִ� ���� �߰�
        lambda x: list(chain(*x)) if all(map(lambda y: isinstance(y, list),x)) else x,
    )    

    return res

def dataToDict_tmp(setDict_f, args, cat=None): ### ����� �����θ� ������ ���
    (datas_perType, hdrs_withIdx) = args
    res = go(
        datas_perType,
        ## 
        map( lambda datas: \
            setDict_f(datas, hdrs_withIdx, cat=cat) if cat=="roomCat" \
            else setDict_f(datas, hdrs_withIdx)
        ), list,
    )
    
    return res

def merge_wmSpecs_sameKey(d:dict):
    pass
    

def match_FamTypeWithCalcType(calcStdTypeDict, allCatFamTypeDict):
    allFamTypeDicts = list(chain(*allCatFamTypeDict))
    res = dictsMerge(allFamTypeDicts)
    
    return res
    pass


calcStdTypeData = get_DataOnRowAreasAtSheet(calcStdSheet, "�����Ǻ�", "#")
#calcStdTypeDict = dataToDict(setDict_OnEachCalType, calcStdTypeData)

#roomFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[0], "Standard Type", "H_")
#roomFamTypeDict = dataToDict(setDict_OnEachFamType, roomFamTypeData, cat="roomCat")
#
#allCatFamTypeData = map( lambda x: get_DataOnRowAreasAtSheet(x, "Standard Type", "H_"), allCatSheets[1:] )
#allCatFamTypeDict = [roomFamTypeDict] + list(map( lambda x: dataToDict(setDict_OnEachFamType, x), allCatFamTypeData ))

#allCatFamType_CalcDict = 

floorsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[1], "Standard Type", "H_")
#floorsFamTypeDict = dataToDict(setDict_OnEachFamType, floorsFamTypeData)
#res = setDict_OnEachFamType(floorsFamTypeData)

#roofsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[2], "Standard Type", "H_")
#roofsFamTypeDict = dataToDict(setDict_OnEachFamType, roofsFamTypeData)
#
#wallsExtFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[3], "Standard Type", "H_")
#wallsExtFamTypeDict = dataToDict(setDict_OnEachFamType, wallsExtFamTypeData)
#
#wallsIntFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[4], "Standard Type", "H_")
#wallsIntFamTypeDict = dataToDict(setDict_OnEachFamType, wallsIntFamTypeData)
#
#stFdnsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[5], "Standard Type", "H_")
#stFdnsFamTypeDict = dataToDict(setDict_OnEachFamType, stFdnsFamTypeData)
#
#stColsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[6], "Standard Type", "H_")
#stColsFamTypeDict = dataToDict(setDict_OnEachFamType, stColsFamTypeData)
#
#stFrmsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[7], "Standard Type", "H_")
#stFrmsFamTypeDict = dataToDict(setDict_OnEachFamType, stFrmsFamTypeData)
#
#ceilingsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[8], "Standard Type", "H_")
#ceilingsFamTypeDict = dataToDict(setDict_OnEachFamType, ceilingsFamTypeData)
#
#doorsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[9], "Standard Type", "H_")
#doorsFamTypeDict = dataToDict(setDict_OnEachFamType, doorsFamTypeData)
#
#windowsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[10], "Standard Type", "H_")
#windowsFamTypeDict = dataToDict(setDict_OnEachFamType, windowsFamTypeData)
#
#stairsFamTypeData = get_DataOnRowAreasAtSheet(allCatSheets[11], "Standard Type", "H_")
#stairsFamTypeDict = dataToDict(setDict_OnEachFamType, stairsFamTypeData)

# Assign your output to the OUT variable.

OUT = calcStdTypeData#match_FamTypeWithCalcType(calcStdTypeDict, allCatFamTypeDict)