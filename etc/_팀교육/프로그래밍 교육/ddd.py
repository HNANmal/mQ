def find_stdWMdicts_inGrp(rowsDictGrp):
    res = go(
        rowsDictGrp, list,
        ## ���� "���������", "Work Master Code" ���� ���� ���� �� ����
        filter(lambda rD: rD["����_���������"] != "" and rD["����_���������"] != ""),
        filter(lambda rD: rD["Work Master Code"] != ""),
        ## Family Type Name�� "H_" ���ڿ� ���Ե� ��� ����
        filter(lambda rD: not findRow_AppliedType(rD, "Family Type Name", rule="H_")),
        ## �� ��ųʸ��� NO, Standard Type ������Ʈ
        map(lambda rD: dictUpdate(rD,{"NO":rowsDictGrp[0]["NO"], "Standard Type":rowsDictGrp[0]["Standard Type"]})),
        ## Q'ty Cal Type Tag ������Ʈ
        map(lambda rD: dictUpdate(rD,{"Q'ty Cal Type Tag":rowsDictGrp[0]["Q'ty Cal Type Tag"]})),
        list,
    )
    return res


def find_stdWMdicts_forCat(rowsDictsGrps):
    res = go(#>
        rowsDictsGrps, list,
        map(find_stdWMdicts_inGrp),
        #filter(lambda x: x!=[]),
        list,
    )#<
    return res