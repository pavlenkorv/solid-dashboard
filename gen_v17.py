import csv, json, math
BASE='/Users/parus/Downloads/Project/solid-dashboard'
UAH=43.85; ACC=19.28; GW=0.018; OP=0.205
CHURN={'B2B':0.073,'B2C':0.18}
TT={'T001':('part-time',70,10.50),'T002':('part-time',70,10.80),'T003':('part-time',70,10.20),
    'T004':('part-time',70,9.90),'T005':('part-time',70,10.00),'T006':('part-time',70,11.00),
    'T007':('part-time',70,10.30),'T008':('part-time',70,9.80),'T009':('part-time',70,10.60),
    'T010':('part-time',70,10.10),'T011':('full-time',100,12.50),'T012':('full-time',100,12.00),
    'T013':('full-time',100,11.80),'T014':('full-time',100,12.20),'T015':('full-time',100,11.50),
    'T016':('full-time',100,11.90),'T017':('part-time',70,10.40),'T018':('part-time',70,9.70),
    'T019':('full-time',100,12.10),'T020':('full-time',100,11.70)}
T_STATUS_MAY={'T013':'pause','T015':'fired'}
PR={'Business Starter':{'seg':'B2B','s':90,'pw':3,'lps':1.5,'pl':9.94,'mo':2,'spm':13,'lpm':19.5},
    'Business C1':{'seg':'B2B','s':60,'pw':3,'lps':1.0,'pl':25.17,'mo':2,'spm':13,'lpm':13.0},
    'IT Starter':{'seg':'B2C','s':90,'pw':2,'lps':1.5,'pl':10.00,'mo':3,'spm':9,'lpm':13.5},
    'IT Basic':{'seg':'B2C','s':90,'pw':2,'lps':1.5,'pl':15.07,'mo':3,'spm':9,'lpm':13.5}}
CAC={'B2B':350,'B2C':200}
f2=lambda v:round(float(v),2); f4=lambda v:round(float(v),4)
pc=lambda m:'green' if m>60 else('orange' if m>30 else 'red')
APR_ASSIGN=[
    ('T001','Business Starter',[9,10,10]),('T002','Business Starter',[10,10,9]),
    ('T003','Business Starter',[9,10,10]),('T004','Business Starter',[10,10,10,10]),
    ('T005','Business Starter',[10,9,10]),('T006','Business Starter',[9,10,10]),
    ('T007','Business Starter',[10,9,10]),('T008','Business Starter',[9,10,10]),
    ('T009','Business Starter',[10,10,9]),('T010','Business Starter',[9,10]),
    ('T011','Business C1',[9,9,9,9,9]),('T012','Business C1',[9,9,9,9,9]),
    ('T013','Business C1',[9,8,9]),('T015','Business C1',[9,9]),
    ('T014','IT Starter',[9,9,9,9]),('T016','IT Basic',[9,9,9,8]),]
MAY_NEW=[('T010','Business Starter',[10]),('T017','Business Starter',[10,10]),
    ('T018','Business Starter',[10]),('T018','IT Starter',[9]),
    ('T019','Business C1',[9]),('T019','IT Starter',[9]),
    ('T020','Business C1',[9]),('T020','IT Basic',[9]),('T016','IT Basic',[9])]
def get_tng(a):
    c={}
    for r in a: c[r[0]]=c.get(r[0],0)+len(r[2])
    return c
def mk_g(mo,tid,prod,gid,stu,acc_v):
    p=PR[prod]; seg=p['seg']; tp,norm,rate=TT[tid]
    lpm=p['lpm']; pl=p['pl']
    rs=f2(pl*lpm); rev=f2(rs*stu); tc=f2(lpm*rate)
    tp_t=f2(tc*.05); tv_t=f2(tc*.01); tt=f2(tp_t+tv_t)
    cpm=f2(CAC[seg]/p['mo']); opex=f2(rev*OP)
    tc10=f2(tc+cpm); pr10=f2(rev-tc10); mg10=f2(pr10/rev*100) if rev else 0
    tc11=f2(tc+cpm+opex+tt+acc_v); pr11=f2(rev-tc11); mg11=f2(pr11/rev*100) if rev else 0
    return {'month':mo,'group_id':'G%04d'%gid,'segment':seg,'course_type':prod,
        'assigned_teacher':tid,'students_count':str(stu),'session_min':str(p['s']),
        'lessons_per_session_60min':str(p['lps']),'sessions_per_week':str(p['pw']),
        'sessions_per_month':str(p['spm']),'lessons_60min_per_month':str(lpm),
        'price_per_session_usd':str(f2(pl*p['lps'])),
        'price_per_lesson_60min_usd':str(pl),'price_per_lesson_60min_uah':str(f2(pl*UAH)),
        'course_usd':str(f2(pl*lpm*p['mo'])),'rev_per_student_pm_usd':str(rs),
        'total_rev_usd':str(rev),'total_rev_uah':str(f2(rev*UAH)),
        'teacher_rate_60min_usd':str(rate),'teacher_cost_rate_usd':str(tc),
        'cac_model':'per_group','cac_group_usd':str(CAC[seg]),'cac_amortized_pm_usd':str(cpm),
        'total_cac_pm_usd':str(cpm),'contract_months':str(p['mo']),
        'teacher_fixed_cost_usd':str(tc),'total_cost_usd':str(tc10),
        'profit_usd':str(pr10),'margin_pct':str(mg10),'breakeven_students':str(f2((tc+cpm+acc_v+tt)/rs) if rs else 0),
        'profitability_color':pc(mg10),'revenue_usd':str(rev),'opex_allocated_usd':str(opex),
        'teacher_tax_pdfo_usd':str(tp_t),'teacher_tax_vz_usd':str(tv_t),
        'teacher_tax_total_usd':str(tt),'accounting_usd':str(f4(acc_v)),
        'total_cost_v11_usd':str(tc11),'profit_v11_usd':str(pr11),
        'margin_v11_pct':str(mg11),'profitability_color_v11':pc(mg11)}
apr_tng=get_tng(APR_ASSIGN); apr_groups=[]; gid=1
for tid,prod,stus in APR_ASSIGN:
    ng=apr_tng[tid]; acc=ACC/ng
    for s in stus: apr_groups.append(mk_g('2025-04',tid,prod,gid,s,acc)); gid+=1
may_tng={}
for tid,prod,stus in APR_ASSIGN:
    eff='T011' if tid=='T013' else ('T019' if tid=='T015' else tid)
    may_tng[eff]=may_tng.get(eff,0)+len(stus)
for tid,prod,stus in MAY_NEW: may_tng[tid]=may_tng.get(tid,0)+len(stus)
may_groups=[]
for g in apr_groups:
    mg=dict(g); mg['month']='2025-05'
    orig_tid=g['assigned_teacher']
    new_tid='T011' if orig_tid=='T013' else ('T019' if orig_tid=='T015' else orig_tid)
    mg['assigned_teacher']=new_tid
    seg=g['segment']; stu_new=max(4,math.floor(int(g['students_count'])*(1-CHURN[seg])))
    ng=may_tng.get(new_tid,1); acc=ACC/ng; rate=TT[new_tid][2]
    mg['teacher_rate_60min_usd']=str(rate)
    lpm=float(g['lessons_60min_per_month']); pl=float(g['price_per_lesson_60min_usd'])
    cpm=float(g['cac_amortized_pm_usd'])
    rs=f2(pl*lpm); rev=f2(rs*stu_new); tc=f2(lpm*rate)
    tp_t=f2(tc*.05); tv_t=f2(tc*.01); tt=f2(tp_t+tv_t); opex=f2(rev*OP)
    tc10=f2(tc+cpm); pr10=f2(rev-tc10); mg10=f2(pr10/rev*100) if rev else 0
    tc11=f2(tc+cpm+opex+tt+acc); pr11=f2(rev-tc11); mg11=f2(pr11/rev*100) if rev else 0
    mg.update({'students_count':str(stu_new),'total_rev_usd':str(rev),'total_rev_uah':str(f2(rev*UAH)),
        'revenue_usd':str(rev),'teacher_cost_rate_usd':str(tc),'teacher_fixed_cost_usd':str(tc),
        'teacher_tax_pdfo_usd':str(tp_t),'teacher_tax_vz_usd':str(tv_t),'teacher_tax_total_usd':str(tt),
        'opex_allocated_usd':str(opex),'accounting_usd':str(f4(acc)),
        'total_cost_usd':str(tc10),'profit_usd':str(pr10),'margin_pct':str(mg10),
        'total_cost_v11_usd':str(tc11),'profit_v11_usd':str(pr11),
        'margin_v11_pct':str(mg11),'profitability_color_v11':pc(mg11)}); may_groups.append(mg)
gid=2001
for tid,prod,stus in MAY_NEW:
    ng=may_tng.get(tid,1); acc=ACC/ng
    for s in stus: may_groups.append(mk_g('2025-05',tid,prod,gid,s,acc)); gid+=1
all_groups=apr_groups+may_groups
for lbl,gx in [('APR',apr_groups),('MAY',may_groups)]:
    b2b=[g for g in gx if g['segment']=='B2B']; b2c=[g for g in gx if g['segment']=='B2C']
    sb2b=sum(int(g['students_count']) for g in b2b); sb2c=sum(int(g['students_count']) for g in b2c)
    grn=sum(1 for g in gx if g['profitability_color_v11']=='green')
    org=sum(1 for g in gx if g['profitability_color_v11']=='orange')
    red=sum(1 for g in gx if g['profitability_color_v11']=='red')
    print(f"{lbl}: {len(gx)}g {sb2b+sb2c}stu B2B={sb2b}({len(b2b)}g) B2C={sb2c}({len(b2c)}g) {sb2b/sb2c:.1f}:1 g={grn} o={org} r={red}")
PR_LPM={'Business Starter':19.5,'Business C1':13.0,'IT Starter':13.5,'IT Basic':13.5}
def calc_l(a):
    ld={}
    for tid,prod,stus in a: ld[tid]=ld.get(tid,0)+len(stus)*PR_LPM[prod]
    return ld
apr_loads=calc_l(APR_ASSIGN)
may_loads={}
for tid,prod,stus in APR_ASSIGN:
    eff='T011' if tid=='T013' else ('T019' if tid=='T015' else tid)
    may_loads[eff]=may_loads.get(eff,0)+len(stus)*PR_LPM[prod]
for tid,v in calc_l(MAY_NEW).items(): may_loads[tid]=may_loads.get(tid,0)+v
APR_T=['T001','T002','T003','T004','T005','T006','T007','T008','T009','T010','T011','T012','T013','T014','T015','T016']
MAY_T=APR_T+['T017','T018','T019','T020']
def mk_t(mo,tid,actual,stat=None):
    tp,norm,rate=TT[tid]; status=stat or 'active'
    if status in ('pause','fired'): actual=0
    actual=round(actual); util=f2(actual/norm*100); diff=actual-norm; dt=''; dc=''
    if util>90: dt='over'; dc='Понаднормове навантаження'
    elif actual==0 and status=='pause': dt='under'; dc='Тимчасово на паузі'
    elif actual==0 and status=='fired': dt='under'; dc='Припинив співпрацю'
    elif actual==0: dt='under'; dc='Без груп у цьому місяці'
    elif util<55: dt='under'; dc='Нижче норми'
    sal=f2(actual*rate); tp_t=f2(sal*.05); tv_t=f2(sal*.01); tt=f2(tp_t+tv_t); tot=f2(sal+tt+ACC)
    return {'month':mo,'teacher_id':tid,'type':tp,'status':status,'max_hours_month':str(norm),
        'norm_lessons_60min_month':str(norm),'actual_lessons_60min':str(actual),'hours_diff':str(diff),
        'deviation_type':dt,'deviation_comment':dc,'utilization_pct':str(util),
        'rate_per_lesson_60min_usd':str(rate),'salary_usd_month':str(sal),
        'salary_uah_month':str(f2(sal*UAH)),'tax_pdfo_usd':str(tp_t),'tax_vz_usd':str(tv_t),
        'tax_total_usd':str(tt),'tax_pdfo_uah':str(int(tp_t*UAH)),'tax_vz_uah':str(int(tv_t*UAH)),
        'tax_total_uah':str(int(tt*UAH)),'accounting_usd':str(ACC),'accounting_uah':str(f2(ACC*UAH)),
        'total_cost_with_tax_usd':str(tot),'total_cost_with_tax_uah':str(int(tot*UAH))}
apr_teachers=[mk_t('2025-04',t,apr_loads.get(t,0)) for t in APR_T]
may_teachers=[mk_t('2025-05',t,may_loads.get(t,0),T_STATUS_MAY.get(t)) for t in MAY_T]
all_teachers=apr_teachers+may_teachers
for t in all_teachers:
    u=float(t['utilization_pct'])
    if u>90 or u<50 or t['status'] in ('pause','fired'):
        print(f"  {t['month']} {t['teacher_id']} {u:.1f}% [{t['status']}]")
def mk_sum(mo,gx,tx):
    rb=f2(sum(float(g['total_rev_usd']) for g in gx if g['segment']=='B2B'))
    rc=f2(sum(float(g['total_rev_usd']) for g in gx if g['segment']=='B2C'))
    rv=f2(rb+rc); gs=f2(sum(float(g['profit_usd']) for g in gx))
    nt=f2(sum(float(g['profit_v11_usd']) for g in gx)); st=sum(int(g['students_count']) for g in gx)
    b2bg=[g for g in gx if g['segment']=='B2B']; b2cg=[g for g in gx if g['segment']=='B2C']
    sb2b=sum(int(g['students_count']) for g in b2bg); sb2c=sum(int(g['students_count']) for g in b2cg)
    grn=sum(1 for g in gx if g['profitability_color_v11']=='green')
    org=sum(1 for g in gx if g['profitability_color_v11']=='orange')
    red=sum(1 for g in gx if g['profitability_color_v11']=='red')
    avg_u=f2(sum(float(t['utilization_pct']) for t in tx)/len(tx))
    return {'month':mo,'active_students':str(st),'active_students_b2b':str(sb2b),'active_students_b2c':str(sb2c),
        'new_students_b2b':'0','new_students_b2c':'0','total_groups':str(len(gx)),
        'b2b_groups':str(len(b2bg)),'b2c_groups':str(len(b2cg)),'b2b_revenue_usd':str(rb),
        'b2c_revenue_usd':str(rc),'total_revenue_usd':str(rv),'total_revenue_uah':str(f2(rv*UAH)),
        'total_profit_usd':str(gs),'avg_margin_pct':str(f2(gs/rv*100) if rv else 0),
        'groups_green':str(grn),'groups_orange':str(org),'groups_red':str(red),
        'avg_teacher_utilization_pct':str(avg_u),'net_profit_v11_usd':str(nt),
        'net_margin_v11_pct':str(f2(nt/rv*100) if rv else 0),
        'opex_fixed_usd':'0','payment_gateway_usd':str(f2(rv*GW))}
summary=[mk_sum('2025-04',apr_groups,apr_teachers),mk_sum('2025-05',may_groups,may_teachers)]
OLBL={'uah_rate':'Курс UAH/USD (ПриватБанк, продаж 02.06.2026)','teachers':'Гонорари+ПДФО+ВЗ+Бухоблік',
    'payroll':'ФОП персонал+ЄСВ','subscriptions':'Підписки','marketing':'Маркетинг','admin':'Адмін/юр',
    'reserve':'Резерв','payment_gateway':'LiqPay/Wayforpay 1.8%','total':'РАЗОМ ОПЕКС'}
OBASE={'payroll':7787,'subscriptions':285,'marketing':1205,'admin':133,'reserve':120}
opex=[]
for mo,gx,tx in [('2025-04',apr_groups,apr_teachers),('2025-05',may_groups,may_teachers)]:
    rv=sum(float(g['total_rev_usd']) for g in gx); tc=round(sum(float(t['total_cost_with_tax_usd']) for t in tx))
    gw=f2(rv*GW); items=dict(OBASE); items['teachers']=tc; items['payment_gateway']=gw; total=f2(sum(items.values()))
    opex.append({'month':mo,'category':OLBL['uah_rate'],'type':'uah_rate','amount_usd':'1.0','amount_uah':str(UAH),'pct_revenue':'—'})
    for tp,cat in list(OLBL.items())[1:]:
        amt=total if tp=='total' else items.get(tp,0)
        opex.append({'month':mo,'category':cat,'type':tp,'amount_usd':str(f2(amt)),'amount_uah':str(int(f2(amt)*UAH)),'pct_revenue':str(f2(amt/rv*100) if rv else 0)})
ret=[]
for mo,gx in [('2025-04',apr_groups),('2025-05',may_groups)]:
    for seg,cs in [('B2B','7,3' if mo=='2025-04' else '6,5'),('B2C','18,0' if mo=='2025-04' else '17,2')]:
        sg=[g for g in gx if g['segment']==seg]; st=sum(int(g['students_count']) for g in sg)
        ret.append({'month':mo,'segment':seg,'active_students':str(st),'new_students':str(int(st*(0.12 if seg=='B2B' else 0.18))),'churn_rate_pct':cs})
prices=[
    {'course_type':'IT Starter','segment':'B2C','session_min':'90','lessons_per_session_60min':'1.5','sessions_in_course':'24','total_lessons_60min_in_course':'36.0','course_usd':'360.0','course_uah':str(round(360*UAH)),'price_per_session_usd':'15.0','price_per_lesson_60min_usd':'10.0','price_per_lesson_60min_uah':str(round(10*UAH,2)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
    {'course_type':'IT Basic','segment':'B2C','session_min':'90','lessons_per_session_60min':'1.5','sessions_in_course':'30','total_lessons_60min_in_course':'45.0','course_usd':'678.15','course_uah':str(round(678.15*UAH)),'price_per_session_usd':'22.605','price_per_lesson_60min_usd':'15.07','price_per_lesson_60min_uah':str(round(15.07*UAH,2)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
    {'course_type':'Business Starter','segment':'B2B','session_min':'90','lessons_per_session_60min':'1.5','sessions_in_course':'26','total_lessons_60min_in_course':'39.0','course_usd':'387.66','course_uah':str(round(387.66*UAH)),'price_per_session_usd':'14.91','price_per_lesson_60min_usd':'9.94','price_per_lesson_60min_uah':str(round(9.94*UAH,2)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
    {'course_type':'Business C1','segment':'B2B','session_min':'60','lessons_per_session_60min':'1.0','sessions_in_course':'32','total_lessons_60min_in_course':'32.0','course_usd':'805.44','course_uah':str(round(805.44*UAH)),'price_per_session_usd':'25.17','price_per_lesson_60min_usd':'25.17','price_per_lesson_60min_uah':str(round(25.17*UAH,2)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
]
cac=[{'month':'2025-04','segment':'B2B','new_clients':'42','budget_usd_min':'7560','budget_usd_mid':'10080','budget_usd_max':'12600','cac_usd_mid':'240','budget_uah_mid':str(round(10080*UAH))},
    {'month':'2025-04','segment':'B2C','new_clients':'7','budget_usd_min':'840','budget_usd_mid':'1120','budget_usd_max':'1400','cac_usd_mid':'160','budget_uah_mid':str(round(1120*UAH))},
    {'month':'2025-05','segment':'B2B','new_clients':'18','budget_usd_min':'3240','budget_usd_mid':'4320','budget_usd_max':'5400','cac_usd_mid':'240','budget_uah_mid':str(round(4320*UAH))},
    {'month':'2025-05','segment':'B2C','new_clients':'3','budget_usd_min':'360','budget_usd_mid':'480','budget_usd_max':'600','cac_usd_mid':'160','budget_uah_mid':str(round(480*UAH))}]
WEEKLY_STU=[
    {'week_start':'2025-03-31','week_label':'Тиж.1 Квіт.','month':'2025-04','total_students':'382','b2b_students':'327','b2c_students':'55','new_enrollments':'43','dropouts':'0'},
    {'week_start':'2025-04-07','week_label':'Тиж.2 Квіт.','month':'2025-04','total_students':'430','b2b_students':'368','b2c_students':'62','new_enrollments':'51','dropouts':'3'},
    {'week_start':'2025-04-14','week_label':'Тиж.3 Квіт.','month':'2025-04','total_students':'468','b2b_students':'401','b2c_students':'67','new_enrollments':'41','dropouts':'3'},
    {'week_start':'2025-04-21','week_label':'Тиж.4 Квіт.','month':'2025-04','total_students':'495','b2b_students':'424','b2c_students':'71','new_enrollments':'30','dropouts':'3'},
    {'week_start':'2025-04-28','week_label':'Тиж.5/Трав.1','month':'2025-05','total_students':'484','b2b_students':'415','b2c_students':'69','new_enrollments':'12','dropouts':'23'},
    {'week_start':'2025-05-05','week_label':'Тиж.2 Трав.','month':'2025-05','total_students':'505','b2b_students':'433','b2c_students':'72','new_enrollments':'28','dropouts':'7'},
    {'week_start':'2025-05-12','week_label':'Тиж.3 Трав.','month':'2025-05','total_students':'522','b2b_students':'448','b2c_students':'74','new_enrollments':'21','dropouts':'4'},
    {'week_start':'2025-05-19','week_label':'Тиж.4 Трав.','month':'2025-05','total_students':'537','b2b_students':'461','b2c_students':'76','new_enrollments':'19','dropouts':'4'},
]
apr_b2b_rev=f2(sum(float(g['total_rev_usd']) for g in apr_groups if g['segment']=='B2B'))
apr_b2c_rev=f2(sum(float(g['total_rev_usd']) for g in apr_groups if g['segment']=='B2C'))
may_b2b_rev=f2(sum(float(g['total_rev_usd']) for g in may_groups if g['segment']=='B2B'))
may_b2c_rev=f2(sum(float(g['total_rev_usd']) for g in may_groups if g['segment']=='B2C'))
apr_lpm=f2(sum(float(g['lessons_60min_per_month']) for g in apr_groups))
may_lpm=f2(sum(float(g['lessons_60min_per_month']) for g in may_groups))
WEEKLY_LOAD=[
    {'month':'2025-04','week':'1','lessons_60min_total':str(f2(apr_lpm*.24)),'revenue_b2b_usd':str(f2(apr_b2b_rev*.24)),'revenue_b2c_usd':str(f2(apr_b2c_rev*.24)),'revenue_total_usd':str(f2((apr_b2b_rev+apr_b2c_rev)*.24))},
    {'month':'2025-04','week':'2','lessons_60min_total':str(f2(apr_lpm*.26)),'revenue_b2b_usd':str(f2(apr_b2b_rev*.26)),'revenue_b2c_usd':str(f2(apr_b2c_rev*.26)),'revenue_total_usd':str(f2((apr_b2b_rev+apr_b2c_rev)*.26))},
    {'month':'2025-04','week':'3','lessons_60min_total':str(f2(apr_lpm*.25)),'revenue_b2b_usd':str(f2(apr_b2b_rev*.25)),'revenue_b2c_usd':str(f2(apr_b2c_rev*.25)),'revenue_total_usd':str(f2((apr_b2b_rev+apr_b2c_rev)*.25))},
    {'month':'2025-04','week':'4','lessons_60min_total':str(f2(apr_lpm*.25)),'revenue_b2b_usd':str(f2(apr_b2b_rev*.25)),'revenue_b2c_usd':str(f2(apr_b2c_rev*.25)),'revenue_total_usd':str(f2((apr_b2b_rev+apr_b2c_rev)*.25))},
    {'month':'2025-05','week':'1','lessons_60min_total':str(f2(may_lpm*.24)),'revenue_b2b_usd':str(f2(may_b2b_rev*.24)),'revenue_b2c_usd':str(f2(may_b2c_rev*.24)),'revenue_total_usd':str(f2((may_b2b_rev+may_b2c_rev)*.24))},
    {'month':'2025-05','week':'2','lessons_60min_total':str(f2(may_lpm*.25)),'revenue_b2b_usd':str(f2(may_b2b_rev*.25)),'revenue_b2c_usd':str(f2(may_b2c_rev*.25)),'revenue_total_usd':str(f2((may_b2b_rev+may_b2c_rev)*.25))},
    {'month':'2025-05','week':'3','lessons_60min_total':str(f2(may_lpm*.26)),'revenue_b2b_usd':str(f2(may_b2b_rev*.26)),'revenue_b2c_usd':str(f2(may_b2c_rev*.26)),'revenue_total_usd':str(f2((may_b2b_rev+may_b2c_rev)*.26))},
    {'month':'2025-05','week':'4','lessons_60min_total':str(f2(may_lpm*.25)),'revenue_b2b_usd':str(f2(may_b2b_rev*.25)),'revenue_b2c_usd':str(f2(may_b2c_rev*.25)),'revenue_total_usd':str(f2((may_b2b_rev+may_b2c_rev)*.25))},
]
FUNNEL=[
    {'week_start':'2025-03-31','week_label':'Тиж.1 Квіт.','month':'2025-04','segment':'B2B','leads_from_ads':'22','trial_lessons':'8','contracts_signed':'4','cr_lead_to_trial_pct':'36.4','cr_trial_to_contract_pct':'50.0','new_students_this_week':'28','groups_starting_this_week':'0','note':''},
    {'week_start':'2025-03-31','week_label':'Тиж.1 Квіт.','month':'2025-04','segment':'B2C','leads_from_ads':'4','trial_lessons':'1','contracts_signed':'0','cr_lead_to_trial_pct':'25.0','cr_trial_to_contract_pct':'0.0','new_students_this_week':'0','groups_starting_this_week':'0','note':''},
    {'week_start':'2025-04-07','week_label':'Тиж.2 Квіт.','month':'2025-04','segment':'B2B','leads_from_ads':'28','trial_lessons':'12','contracts_signed':'6','cr_lead_to_trial_pct':'42.9','cr_trial_to_contract_pct':'50.0','new_students_this_week':'38','groups_starting_this_week':'0','note':''},
    {'week_start':'2025-04-07','week_label':'Тиж.2 Квіт.','month':'2025-04','segment':'B2C','leads_from_ads':'5','trial_lessons':'2','contracts_signed':'1','cr_lead_to_trial_pct':'40.0','cr_trial_to_contract_pct':'50.0','new_students_this_week':'4','groups_starting_this_week':'0','note':''},
    {'week_start':'2025-04-14','week_label':'Тиж.3 Квіт.','month':'2025-04','segment':'B2B','leads_from_ads':'35','trial_lessons':'16','contracts_signed':'8','cr_lead_to_trial_pct':'45.7','cr_trial_to_contract_pct':'50.0','new_students_this_week':'48','groups_starting_this_week':'4','note':'Старт 4 нових груп BS'},
    {'week_start':'2025-04-14','week_label':'Тиж.3 Квіт.','month':'2025-04','segment':'B2C','leads_from_ads':'6','trial_lessons':'2','contracts_signed':'1','cr_lead_to_trial_pct':'33.3','cr_trial_to_contract_pct':'50.0','new_students_this_week':'4','groups_starting_this_week':'0','note':''},
    {'week_start':'2025-04-21','week_label':'Тиж.4 Квіт.','month':'2025-04','segment':'B2B','leads_from_ads':'42','trial_lessons':'18','contracts_signed':'9','cr_lead_to_trial_pct':'42.9','cr_trial_to_contract_pct':'50.0','new_students_this_week':'36','groups_starting_this_week':'2','note':''},
    {'week_start':'2025-04-21','week_label':'Тиж.4 Квіт.','month':'2025-04','segment':'B2C','leads_from_ads':'7','trial_lessons':'3','contracts_signed':'1','cr_lead_to_trial_pct':'42.9','cr_trial_to_contract_pct':'33.3','new_students_this_week':'4','groups_starting_this_week':'1','note':''},
    {'week_start':'2025-04-28','week_label':'Тиж.5/Трав.1','month':'2025-05','segment':'B2B','leads_from_ads':'38','trial_lessons':'17','contracts_signed':'8','cr_lead_to_trial_pct':'44.7','cr_trial_to_contract_pct':'47.1','new_students_this_week':'32','groups_starting_this_week':'2','note':'T017 нові групи BS'},
    {'week_start':'2025-04-28','week_label':'Тиж.5/Трав.1','month':'2025-05','segment':'B2C','leads_from_ads':'6','trial_lessons':'2','contracts_signed':'1','cr_lead_to_trial_pct':'33.3','cr_trial_to_contract_pct':'50.0','new_students_this_week':'5','groups_starting_this_week':'1','note':''},
    {'week_start':'2025-05-05','week_label':'Тиж.2 Трав.','month':'2025-05','segment':'B2B','leads_from_ads':'28','trial_lessons':'12','contracts_signed':'6','cr_lead_to_trial_pct':'42.9','cr_trial_to_contract_pct':'50.0','new_students_this_week':'24','groups_starting_this_week':'2','note':'T018 BS, T019 BC1'},
    {'week_start':'2025-05-05','week_label':'Тиж.2 Трав.','month':'2025-05','segment':'B2C','leads_from_ads':'5','trial_lessons':'2','contracts_signed':'1','cr_lead_to_trial_pct':'40.0','cr_trial_to_contract_pct':'50.0','new_students_this_week':'4','groups_starting_this_week':'1','note':'T018 ITS'},
    {'week_start':'2025-05-12','week_label':'Тиж.3 Трав.','month':'2025-05','segment':'B2B','leads_from_ads':'22','trial_lessons':'10','contracts_signed':'5','cr_lead_to_trial_pct':'45.5','cr_trial_to_contract_pct':'50.0','new_students_this_week':'20','groups_starting_this_week':'1','note':'T020 BC1'},
    {'week_start':'2025-05-12','week_label':'Тиж.3 Трав.','month':'2025-05','segment':'B2C','leads_from_ads':'4','trial_lessons':'2','contracts_signed':'1','cr_lead_to_trial_pct':'50.0','cr_trial_to_contract_pct':'50.0','new_students_this_week':'4','groups_starting_this_week':'1','note':'T016 ITB'},
    {'week_start':'2025-05-19','week_label':'Тиж.4 Трав.','month':'2025-05','segment':'B2B','leads_from_ads':'18','trial_lessons':'8','contracts_signed':'4','cr_lead_to_trial_pct':'44.4','cr_trial_to_contract_pct':'50.0','new_students_this_week':'16','groups_starting_this_week':'0','note':''},
    {'week_start':'2025-05-19','week_label':'Тиж.4 Трав.','month':'2025-05','segment':'B2C','leads_from_ads':'3','trial_lessons':'1','contracts_signed':'0','cr_lead_to_trial_pct':'33.3','cr_trial_to_contract_pct':'0.0','new_students_this_week':'0','groups_starting_this_week':'0','note':''},
]
def wcsv(path,rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
wcsv(BASE+'/01_price_normalization_v17.csv',prices)
wcsv(BASE+'/02_monthly_summary_v17.csv',summary)
wcsv(BASE+'/03_groups_v17.csv',all_groups)
wcsv(BASE+'/04_teachers_v17.csv',all_teachers)
wcsv(BASE+'/06_retention_v17.csv',ret)
wcsv(BASE+'/07_cac_v17.csv',cac)
wcsv(BASE+'/08_opex_dataset_v17.csv',opex)
wcsv(BASE+'/09_sales_funnel_weekly_v17.csv',FUNNEL)
wcsv(BASE+'/05_weekly_load_v17.csv',WEEKLY_LOAD)
wcsv(BASE+'/10_weekly_students_v17.csv',WEEKLY_STU)
D_out={'prices':prices,'summary':summary,'groups':all_groups,'teachers':all_teachers,
       'opex':opex,'retention':ret,'cac':cac,'funnel':FUNNEL,
       'weekly_students':WEEKLY_STU,'weekly_load':WEEKLY_LOAD}
with open(BASE+'/v17_data.json','w',encoding='utf-8') as f:
    json.dump(D_out,f,ensure_ascii=False,separators=(',',':'))
errors=0
for g in all_groups:
    rv=float(g['total_rev_usd']); pr10=float(g['profit_usd']); tc10=float(g['total_cost_usd'])
    pr11=float(g['profit_v11_usd']); tc11=float(g['total_cost_v11_usd'])
    if abs(rv-pr10-tc10)>0.02: print(f"ERR v10 {g['group_id']}"); errors+=1
    if abs(rv-pr11-tc11)>0.02: print(f"ERR v11 {g['group_id']}"); errors+=1
    if tc11<tc10: print(f"ERR tc11<tc10 {g['group_id']}"); errors+=1
print(f"Errors: {errors}")
for s in summary:
    print(f"{s['month']}: {s['active_students']}stu rev=${s['total_revenue_usd']} net=${s['net_profit_v11_usd']}({s['net_margin_v11_pct']}%)")
print("DONE v17")
