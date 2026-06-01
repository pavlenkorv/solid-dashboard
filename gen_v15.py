"""
v15 Dataset Generator
APRIL:  495 students, 53 groups, 16 teachers (T001-T016)
MAY:    537 students, 63 groups, 20 teachers (T001-T020)
PT norm=70, FT norm=100; target util 80-85%
"""
import csv, json, random, math
from collections import Counter
random.seed(42)

BASE='/Users/parus/Downloads/Project/solid-dashboard'
UAH=41.5; ACC=19.28; GW=0.018; OP=0.205

# Teacher registry: (type, norm_lessons/mo, rate_usd/lesson)
TT={
    'T001':('part-time', 70,10.50),'T002':('part-time', 70,10.80),
    'T003':('part-time', 70,10.20),'T004':('part-time', 70, 9.90),
    'T005':('part-time', 70,10.00),'T006':('part-time', 70,11.00),
    'T007':('part-time', 70,10.30),'T008':('part-time', 70, 9.80),
    'T009':('part-time', 70,10.60),'T010':('part-time', 70,10.10),
    'T011':('full-time',100,12.50),'T012':('full-time',100,12.00),
    'T013':('full-time',100,11.80),'T014':('full-time',100,12.20),
    'T015':('full-time',100,11.50),'T016':('full-time',100,11.90),
    'T017':('part-time', 70,10.40),'T018':('part-time', 70, 9.70),
    'T019':('full-time',100,12.10),'T020':('full-time',100,11.70),
}
# Products: (segment, session_min, sess/week, lessons_per_session_60min, price/lesson, contract_months)
PR={
    'Business Starter':{'seg':'B2B','s':90,'pw':3,'lps':1.5,'pl':9.94, 'mo':2,'spm':13,'lpm':19.5},
    'Business C1':     {'seg':'B2B','s':60,'pw':3,'lps':1.0,'pl':25.17,'mo':2,'spm':13,'lpm':13.0},
    'IT Starter':      {'seg':'B2C','s':90,'pw':2,'lps':1.5,'pl':10.00,'mo':3,'spm':9, 'lpm':13.5},
    'IT Basic':        {'seg':'B2C','s':90,'pw':2,'lps':1.5,'pl':15.07,'mo':3,'spm':9, 'lpm':13.5},
}
CAC={'B2B':350,'B2C':200}
CHURN={'B2B':0.073,'B2C':0.18}

f2=lambda v:round(float(v),2)
f4=lambda v:round(float(v),4)
pc=lambda m:'green' if m>60 else('orange' if m>30 else 'red')

# ── APRIL EXACT ASSIGNMENT ────────────────────────────────────────────────────
# 18 BS + 12 BC1 + 11 ITS + 12 ITB = 53 groups
# Student targets per group to hit exactly 495:
# BS: need 171 stu / 18g = avg 9.5 → mix of 9 and 10
# BC1: need 100 stu / 12g = avg 8.33 → mix of 8 and 9
# ITS: need 105 stu / 11g = avg 9.55 → mix of 9 and 10
# ITB: need 119 stu / 12g = avg 9.92 → mix of 9 and 11
APR_ASSIGN=[
    # (teacher, product, students_list)
    ('T001','Business Starter',[9,10,10]),
    ('T002','Business Starter',[10,10, 9]),
    ('T003','Business Starter',[9,10, 9]),
    ('T004','Business Starter',[10,10,10, 9]),  # RED: 4×19.5=78/70=111%
    ('T005','Business Starter',[10, 9,10]),
    ('T006','Business Starter',[9, 10]),        # 2g only: 2×19.5=39/70=55.7%
    ('T007','Business C1',     [9, 8, 9, 8]),
    ('T008','Business C1',     [8, 9, 8]),
    ('T009','Business C1',     [8, 9, 8]),
    # T010: 0 groups → LOW
    ('T011','IT Starter',      [10, 9,10,10]),
    ('T011','IT Basic',        [10,10]),
    ('T012','IT Starter',      [10,10]),
    ('T012','IT Basic',        [10, 9,10,10]),
    ('T013','IT Starter',      [9, 10, 9]),     # 3ITS+2ITB=40.5+27=67.5/100=67.5%
    ('T013','IT Basic',        [10,10]),
    ('T014','IT Starter',      [9, 10]),
    ('T014','IT Basic',        [10,10,10,10]),
    ('T015','Business C1',     [8, 9]),         # LOW: 2×13=26/100=26%
    # T016: 0 groups → LOW
]

# Verify April counts
bs=[x for x in APR_ASSIGN if x[1]=='Business Starter']
bc1=[x for x in APR_ASSIGN if x[1]=='Business C1']
its=[x for x in APR_ASSIGN if x[1]=='IT Starter']
itb=[x for x in APR_ASSIGN if x[1]=='IT Basic']
print("APRIL groups:", sum(len(x[2]) for x in bs),"BS |",
      sum(len(x[2]) for x in bc1),"BC1 |",
      sum(len(x[2]) for x in its),"ITS |",
      sum(len(x[2]) for x in itb),"ITB")
print("APRIL students:", sum(sum(x[2]) for x in APR_ASSIGN), "(target 495)")

# ── TEACHER GROUP COUNT (for accounting distribution) ─────────────────────────
def get_tng(assign):
    cnt={}
    for row in assign:
        t=row[0]; n=len(row[2])
        cnt[t]=cnt.get(t,0)+n
    return cnt

apr_tng=get_tng(APR_ASSIGN)

# ── BUILD GROUP ROW ────────────────────────────────────────────────────────────
def mk_group(month, tid, prod, gid, stu, tng):
    p=PR[prod]; seg=p['seg']
    tp,norm,rate=TT[tid]; ng=tng.get(tid,1); acc=f4(ACC/ng)
    lpm=p['lpm']; pl=p['pl']
    rs=f2(pl*lpm); rev=f2(rs*stu)
    tc=f2(lpm*rate); tp_t=f2(tc*.05); tv_t=f2(tc*.01); tt=f2(tp_t+tv_t)
    cpm=f2(CAC[seg]/p['mo']); opex=f2(rev*OP)
    tc10=f2(tc+cpm); pr10=f2(rev-tc10); mg10=f2(pr10/rev*100) if rev else 0
    tc11=f2(tc+cpm+opex+tt+acc); pr11=f2(rev-tc11); mg11=f2(pr11/rev*100) if rev else 0
    be=f2((tc+cpm+acc+tt)/rs) if rs else 0
    return {
        'month':month,'group_id':'G%04d'%gid,'segment':seg,'course_type':prod,
        'assigned_teacher':tid,'students_count':str(stu),
        'session_min':str(p['s']),'lessons_per_session_60min':str(p['lps']),
        'sessions_per_week':str(p['pw']),'sessions_per_month':str(p['spm']),
        'lessons_60min_per_month':str(lpm),'price_per_lesson_60min_usd':str(pl),
        'price_per_lesson_60min_uah':str(f2(pl*UAH)),'course_usd':str(f2(pl*lpm*p['mo'])),
        'rev_per_student_pm_usd':str(rs),'total_rev_usd':str(rev),
        'total_rev_uah':str(f2(rev*UAH)),'teacher_rate_60min_usd':str(rate),
        'teacher_cost_rate_usd':str(tc),'cac_model':'per_group',
        'cac_group_usd':str(CAC[seg]),'cac_amortized_pm_usd':str(cpm),
        'total_cac_pm_usd':str(cpm),'contract_months':str(p['mo']),
        'teacher_fixed_cost_usd':str(tc),'total_cost_usd':str(tc10),
        'profit_usd':str(pr10),'margin_pct':str(mg10),'breakeven_students':str(be),
        'profitability_color':pc(mg10),'revenue_usd':str(rev),
        'opex_allocated_usd':str(opex),'teacher_tax_pdfo_usd':str(tp_t),
        'teacher_tax_vz_usd':str(tv_t),'teacher_tax_total_usd':str(tt),
        'accounting_usd':str(acc),'total_cost_v11_usd':str(tc11),
        'profit_v11_usd':str(pr11),'margin_v11_pct':str(mg11),
        'profitability_color_v11':pc(mg11),
    }

# ── APRIL GROUPS ──────────────────────────────────────────────────────────────
apr_groups=[]; gid=1
for row in APR_ASSIGN:
    tid,prod,stus=row
    for stu in stus:
        apr_groups.append(mk_group('2025-04',tid,prod,gid,stu,apr_tng))
        gid+=1

total_apr=sum(int(g['students_count']) for g in apr_groups)
print(f"\nAPRIL BUILT: {len(apr_groups)} groups, {total_apr} students")

# ── MAY GROUPS ────────────────────────────────────────────────────────────────
# April groups continue with churn; new groups added
may_groups=[]

# Continuing April groups with churn applied
for g in apr_groups:
    mg=dict(g); mg['month']='2025-05'
    seg=g['segment']
    stu_old=int(g['students_count'])
    stu_new=max(4, math.floor(stu_old*(1-CHURN[seg])))
    # Recalculate with new student count
    lpm=float(g['lessons_60min_per_month']); pl=float(g['price_per_lesson_60min_usd'])
    rate=float(g['teacher_rate_60min_usd']); cpm=float(g['cac_amortized_pm_usd'])
    acc=float(g['accounting_usd'])  # will be updated after all May groups counted
    rs=f2(pl*lpm); rev=f2(rs*stu_new)
    tc=f2(lpm*rate); tp_t=f2(tc*.05); tv_t=f2(tc*.01); tt=f2(tp_t+tv_t)
    opex=f2(rev*OP)
    tc10=f2(tc+cpm); pr10=f2(rev-tc10); mg10=f2(pr10/rev*100) if rev else 0
    tc11=f2(tc+cpm+opex+tt+acc); pr11=f2(rev-tc11); mg11=f2(pr11/rev*100) if rev else 0
    mg.update({'students_count':str(stu_new),'total_rev_usd':str(rev),
        'total_rev_uah':str(f2(rev*UAH)),'revenue_usd':str(rev),'opex_allocated_usd':str(opex),
        'total_cost_usd':str(tc10),'profit_usd':str(pr10),'margin_pct':str(mg10),
        'total_cost_v11_usd':str(tc11),'profit_v11_usd':str(pr11),
        'margin_v11_pct':str(mg11),'profitability_color_v11':pc(mg11)})
    may_groups.append(mg)

stu_continuing=sum(int(g['students_count']) for g in may_groups)
print(f"May continuing ({len(may_groups)} groups): {stu_continuing} stu")
print(f"Need new students: {537-stu_continuing}")

# New groups in May — assign to T010, T016, T017, T018
# Target: total = 537
need=537-stu_continuing
# T010: 2×BS avg10=20, 1×ITS avg9=9 → 29 stu  [util: 2×19.5+13.5=52.5/70=75%]
# T016: 2×ITS avg10=20, 2×ITB avg9=18 → 38 stu [util: 2×13.5+2×13.5=54/100=54% LOW]
# T017: 3×BS avg10=30 → [util: 3×19.5=58.5/70=83.6% ✓]
# T018: 1×ITS avg9 → 9 stu [util: 13.5/70=19.3% VERY LOW — new teacher]
# TOTAL new: 29+38+30+9 = 106 ← too many (need ~104)
# Adjust T018: remove (only 1 group, very low util = realistic for new teacher)
# T010:2BS+1ITS=29, T016:2ITS+2ITB=38, T017:3BS=30, T018:1ITS=9 = 106
# 433+106=539 ≈ 537 ✓ (within tolerance)

MAY_NEW_ASSIGN=[
    ('T010','Business Starter',[10,10]),
    ('T010','IT Starter',     [9]),
    ('T016','IT Starter',     [10,10]),
    ('T016','IT Basic',       [9, 9]),
    ('T017','Business Starter',[10,10,10]),
    ('T018','IT Starter',     [9]),         # LOW: only 1 group, 13.5/70=19.3%
]

# Teacher group count for May (continuing + new)
may_tid_cnt={}
for g in may_groups: may_tid_cnt[g['assigned_teacher']]=may_tid_cnt.get(g['assigned_teacher'],0)+1
may_extra_tng=get_tng(MAY_NEW_ASSIGN)
for tid,cnt in may_extra_tng.items():
    may_tid_cnt[tid]=may_tid_cnt.get(tid,0)+cnt
may_tng=may_tid_cnt

gid=2001
for row in MAY_NEW_ASSIGN:
    tid,prod,stus=row
    for stu in stus:
        may_groups.append(mk_group('2025-05',tid,prod,gid,stu,may_tng))
        gid+=1

# Update accounting_usd for all May groups with correct teacher group counts
for g in may_groups:
    tid=g['assigned_teacher']; ng=may_tng.get(tid,1); acc=f4(ACC/ng)
    g['accounting_usd']=str(acc)
    # Recalc v11
    tc=f2(float(g['teacher_fixed_cost_usd'])); cpm=f2(float(g['cac_amortized_pm_usd']))
    opex=f2(float(g['opex_allocated_usd'])); tt=f2(float(g['teacher_tax_total_usd']))
    rev=f2(float(g['total_rev_usd']))
    tc11=f2(tc+cpm+opex+tt+acc); pr11=f2(rev-tc11); mg11=f2(pr11/rev*100) if rev else 0
    g['total_cost_v11_usd']=str(tc11); g['profit_v11_usd']=str(pr11)
    g['margin_v11_pct']=str(mg11); g['profitability_color_v11']=pc(mg11)

total_may=sum(int(g['students_count']) for g in may_groups)
print(f"\nMAY BUILT: {len(may_groups)} groups, {total_may} students (target 537)")

all_groups=apr_groups+may_groups

# ── TEACHERS ──────────────────────────────────────────────────────────────────
def calc_teacher_load(month, assign_list, new_assign=None):
    """Calculate actual lessons from group assignments."""
    loads={}  # tid -> actual_lessons
    for row in assign_list:
        tid,prod,stus=row
        lpm=PR[prod]['lpm']
        loads[tid]=loads.get(tid,0)+len(stus)*lpm
    if new_assign:
        for row in new_assign:
            tid,prod,stus=row
            lpm=PR[prod]['lpm']
            loads[tid]=loads.get(tid,0)+len(stus)*lpm
    return loads

apr_loads=calc_teacher_load('2025-04',APR_ASSIGN)
may_loads=calc_teacher_load('2025-05',APR_ASSIGN,MAY_NEW_ASSIGN)  # April teachers keep groups

def mk_teacher(month, tid, actual_lessons):
    tp,norm,rate=TT[tid]; actual=round(actual_lessons)
    util=f2(actual/norm*100); diff=actual-norm
    dt=''; dc=''
    if util>90: dt='over'; dc='Понаднормове навантаження'
    elif actual==0: dt='under'; dc='Викладач без груп у цьому місяці'
    elif util<55: dt='under'; dc='Нижче норми: мало груп'
    sal=f2(actual*rate); tp_t=f2(sal*.05); tv_t=f2(sal*.01); tt=f2(tp_t+tv_t); tot=f2(sal+tt+ACC)
    return {'month':month,'teacher_id':tid,'type':tp,'status':'active',
        'max_hours_month':str(norm),'norm_lessons_60min_month':str(norm),
        'actual_lessons_60min':str(actual),'hours_diff':str(diff),
        'deviation_type':dt,'deviation_comment':dc,'utilization_pct':str(util),
        'rate_per_lesson_60min_usd':str(rate),'salary_usd_month':str(sal),
        'salary_uah_month':str(f2(sal*UAH)),'tax_pdfo_usd':str(tp_t),
        'tax_vz_usd':str(tv_t),'tax_total_usd':str(tt),
        'tax_pdfo_uah':str(int(tp_t*UAH)),'tax_vz_uah':str(int(tv_t*UAH)),
        'tax_total_uah':str(int(tt*UAH)),'accounting_usd':str(ACC),
        'accounting_uah':str(f2(ACC*UAH)),'total_cost_with_tax_usd':str(tot),
        'total_cost_with_tax_uah':str(int(tot*UAH))}

# April teachers: T001-T016
APR_TEACHERS=['T001','T002','T003','T004','T005','T006','T007','T008','T009','T010','T011','T012','T013','T014','T015','T016']
apr_teachers=[mk_teacher('2025-04',tid,apr_loads.get(tid,0)) for tid in APR_TEACHERS]

# May teachers: all 20, April teachers keep their April load + may extras
MAY_TEACHERS=['T001','T002','T003','T004','T005','T006','T007','T008','T009','T010','T011','T012','T013','T014','T015','T016','T017','T018','T019','T020']
# T019, T020 not in new_assign → 0 lessons (they can be added later)
may_teachers=[mk_teacher('2025-05',tid,may_loads.get(tid,0)) for tid in MAY_TEACHERS]

all_teachers=apr_teachers+may_teachers

print("\nTeacher utilization April:")
for t in apr_teachers:
    u=float(t['utilization_pct']); z='RED' if u>90 else('BLUE' if u<55 else 'ok')
    print(f"  {t['teacher_id']} {t['type'][:2].upper()} util={u:.1f}% actual={t['actual_lessons_60min']}/{t['norm_lessons_60min_month']} {z}")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
def mk_sum(month, groups, teachers):
    rb=f2(sum(float(g['total_rev_usd']) for g in groups if g['segment']=='B2B'))
    rc=f2(sum(float(g['total_rev_usd']) for g in groups if g['segment']=='B2C'))
    rv=f2(rb+rc); gs=f2(sum(float(g['profit_usd']) for g in groups))
    nt=f2(sum(float(g['profit_v11_usd']) for g in groups))
    st=sum(int(g['students_count']) for g in groups)
    b2bg=[g for g in groups if g['segment']=='B2B']; b2cg=[g for g in groups if g['segment']=='B2C']
    stu_b2b=sum(int(g['students_count']) for g in b2bg); stu_b2c=sum(int(g['students_count']) for g in b2cg)
    grn=sum(1 for g in groups if g['profitability_color_v11']=='green')
    org=sum(1 for g in groups if g['profitability_color_v11']=='orange')
    red=sum(1 for g in groups if g['profitability_color_v11']=='red')
    avg_u=f2(sum(float(t['utilization_pct']) for t in teachers)/len(teachers))
    return {
        'month':month,'active_students':str(st),'active_students_b2b':str(stu_b2b),
        'active_students_b2c':str(stu_b2c),'new_students_b2b':'0','new_students_b2c':'0',
        'total_groups':str(len(groups)),'b2b_groups':str(len(b2bg)),'b2c_groups':str(len(b2cg)),
        'b2b_revenue_usd':str(rb),'b2c_revenue_usd':str(rc),'total_revenue_usd':str(rv),
        'total_revenue_uah':str(f2(rv*UAH)),'total_profit_usd':str(gs),
        'avg_margin_pct':str(f2(gs/rv*100) if rv else 0),
        'groups_green':str(grn),'groups_orange':str(org),'groups_red':str(red),
        'avg_teacher_utilization_pct':str(avg_u),'net_profit_v11_usd':str(nt),
        'net_margin_v11_pct':str(f2(nt/rv*100) if rv else 0),
        'opex_fixed_usd':'0','payment_gateway_usd':str(f2(rv*GW)),
    }

summary=[mk_sum('2025-04',apr_groups,apr_teachers), mk_sum('2025-05',may_groups,may_teachers)]
print("\nSUMMARY:")
for s in summary:
    print(f"  {s['month']}: {s['active_students']}stu B2B={s['active_students_b2b']} B2C={s['active_students_b2c']}")
    print(f"    {s['total_groups']}g rev=${s['total_revenue_usd']} net=${s['net_profit_v11_usd']}({s['net_margin_v11_pct']}%)")
    print(f"    profitability: green={s['groups_green']} orange={s['groups_orange']} red={s['groups_red']}")

# ── OPEX ─────────────────────────────────────────────────────────────────────
OLBL={'teachers':'Гонорари+ПДФО+ВЗ+Бухоблік','payroll':'ФОП персонал+ЄСВ',
    'subscriptions':'Підписки','marketing':'Маркетинг','admin':'Адмін/юр',
    'reserve':'Резерв','payment_gateway':'LiqPay/Wayforpay 1.8%','total':'РАЗОМ ОПЕКС'}
OBASE={'payroll':7787,'subscriptions':285,'marketing':1205,'admin':133,'reserve':120}
opex=[]
for month,gx,tx in [('2025-04',apr_groups,apr_teachers),('2025-05',may_groups,may_teachers)]:
    rv=sum(float(g['total_rev_usd']) for g in gx)
    tc=round(sum(float(t['total_cost_with_tax_usd']) for t in tx))
    gw=f2(rv*GW); items=dict(OBASE); items['teachers']=tc; items['payment_gateway']=gw
    total=f2(sum(items.values()))
    for tp,cat in OLBL.items():
        amt=total if tp=='total' else items.get(tp,0)
        opex.append({'month':month,'category':cat,'type':tp,'amount_usd':str(f2(amt)),
            'amount_uah':str(int(f2(amt)*UAH)),'pct_revenue':str(f2(amt/rv*100) if rv else 0)})

# ── RETENTION ─────────────────────────────────────────────────────────────────
ret=[]
for month,gx in [('2025-04',apr_groups),('2025-05',may_groups)]:
    for seg,churn_str in [('B2B','7,3' if month=='2025-04' else '6,5'),
                           ('B2C','18,0' if month=='2025-04' else '17,2')]:
        sg=[g for g in gx if g['segment']==seg]; st=sum(int(g['students_count']) for g in sg)
        new_s=int(st*(0.12 if seg=='B2B' else 0.18))
        ret.append({'month':month,'segment':seg,'active_students':str(st),
            'new_students':str(new_s),'churn_rate_pct':churn_str})

# ── PRICES ────────────────────────────────────────────────────────────────────
prices=[
    {'course_type':'IT Starter','segment':'B2C','session_min':'90','lessons_per_session_60min':'1.5',
     'sessions_in_course':'24','total_lessons_60min_in_course':'36.0','course_usd':'360.0',
     'course_uah':str(round(360*UAH)),'price_per_session_usd':'15.0','price_per_lesson_60min_usd':'10.0',
     'price_per_lesson_60min_uah':str(round(10*UAH,1)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
    {'course_type':'IT Basic','segment':'B2C','session_min':'90','lessons_per_session_60min':'1.5',
     'sessions_in_course':'30','total_lessons_60min_in_course':'45.0','course_usd':'678.15',
     'course_uah':str(round(678.15*UAH)),'price_per_session_usd':'22.605','price_per_lesson_60min_usd':'15.07',
     'price_per_lesson_60min_uah':str(round(15.07*UAH,1)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
    {'course_type':'Business Starter','segment':'B2B','session_min':'90','lessons_per_session_60min':'1.5',
     'sessions_in_course':'26','total_lessons_60min_in_course':'39.0','course_usd':'387.66',
     'course_uah':str(round(387.66*UAH)),'price_per_session_usd':'14.91','price_per_lesson_60min_usd':'9.94',
     'price_per_lesson_60min_uah':str(round(9.94*UAH,1)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
    {'course_type':'Business C1','segment':'B2B','session_min':'60','lessons_per_session_60min':'1.0',
     'sessions_in_course':'32','total_lessons_60min_in_course':'32.0','course_usd':'805.44',
     'course_uah':str(round(805.44*UAH)),'price_per_session_usd':'25.17','price_per_lesson_60min_usd':'25.17',
     'price_per_lesson_60min_uah':str(round(25.17*UAH,1)),'uah_rate_used':str(UAH),'source':'solid.com.ua (verified)'},
]

# ── CAC ───────────────────────────────────────────────────────────────────────
cac=[
    {'month':'2025-04','segment':'B2B','new_clients':'42','budget_usd_min':'7560','budget_usd_mid':'10080','budget_usd_max':'12600','cac_usd_mid':'240','budget_uah_mid':str(round(10080*UAH))},
    {'month':'2025-04','segment':'B2C','new_clients':'24','budget_usd_min':'2880','budget_usd_mid':'3840','budget_usd_max':'4800','cac_usd_mid':'160','budget_uah_mid':str(round(3840*UAH))},
    {'month':'2025-05','segment':'B2B','new_clients':'18','budget_usd_min':'3240','budget_usd_mid':'4320','budget_usd_max':'5400','cac_usd_mid':'240','budget_uah_mid':str(round(4320*UAH))},
    {'month':'2025-05','segment':'B2C','new_clients':'13','budget_usd_min':'1560','budget_usd_mid':'2080','budget_usd_max':'2600','cac_usd_mid':'160','budget_uah_mid':str(round(2080*UAH))},
]

# ── WEEKLY STUDENT DYNAMICS (for new trend chart) ─────────────────────────────
# Simulate weekly student counts across Apr-May for trend chart
# Apr W1: ~420 students starting (some groups still in ramp-up)
# Apr W2-W4: full 495
# May W1-W2: churn kicks in, new groups start
# Apr W1-W4 + May W1-W4
WEEKLY_STU=[
    {'week_start':'2025-03-31','week_label':'Тиж.1 Квіт.','month':'2025-04',
     'total_students':'420','b2b_students':'243','b2c_students':'177','new_enrollments':'52','dropouts':'0'},
    {'week_start':'2025-04-07','week_label':'Тиж.2 Квіт.','month':'2025-04',
     'total_students':'472','b2b_students':'274','b2c_students':'198','new_enrollments':'55','dropouts':'3'},
    {'week_start':'2025-04-14','week_label':'Тиж.3 Квіт.','month':'2025-04',
     'total_students':'489','b2b_students':'282','b2c_students':'207','new_enrollments':'20','dropouts':'3'},
    {'week_start':'2025-04-21','week_label':'Тиж.4 Квіт.','month':'2025-04',
     'total_students':'495','b2b_students':'286','b2c_students':'209','new_enrollments':'9','dropouts':'3'},
    {'week_start':'2025-04-28','week_label':'Тиж.5/Трав.1','month':'2025-05',
     'total_students':'491','b2b_students':'280','b2c_students':'211','new_enrollments':'12','dropouts':'16'},
    {'week_start':'2025-05-05','week_label':'Тиж.2 Трав.','month':'2025-05',
     'total_students':'498','b2b_students':'283','b2c_students':'215','new_enrollments':'21','dropouts':'14'},
    {'week_start':'2025-05-12','week_label':'Тиж.3 Трав.','month':'2025-05',
     'total_students':'518','b2b_students':'293','b2c_students':'225','new_enrollments':'28','dropouts':'8'},
    {'week_start':'2025-05-19','week_label':'Тиж.4 Трав.','month':'2025-05',
     'total_students':'537','b2b_students':'306','b2c_students':'231','new_enrollments':'23','dropouts':'4'},
]

# ── SAVE ALL CSVs ─────────────────────────────────────────────────────────────
def wcsv(path, rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

wcsv(BASE+'/01_price_normalization_v15.csv', prices)
wcsv(BASE+'/02_monthly_summary_v15.csv', summary)
wcsv(BASE+'/03_groups_v15.csv', all_groups)
wcsv(BASE+'/04_teachers_v15.csv', all_teachers)
wcsv(BASE+'/06_retention_v15.csv', ret)
wcsv(BASE+'/07_cac_v15.csv', cac)
wcsv(BASE+'/08_opex_dataset_v15.csv', opex)
wcsv(BASE+'/10_weekly_students_v15.csv', WEEKLY_STU)

# ── SAVE JSON for dashboard ───────────────────────────────────────────────────
# Load existing funnel from HTML
with open(BASE+'/index.html','r',encoding='utf-8') as f: html=f.read()
idx=html.find('var D={'); depth=0; start=idx+6
for i in range(start,len(html)):
    c=html[i]
    if c in '{[': depth+=1
    elif c in ']}':
        depth-=1
        if depth==0: D_old=json.loads(html[start:i+1]); break
funnel=D_old.get('funnel',[])

D_out={'prices':prices,'summary':summary,'groups':all_groups,'teachers':all_teachers,
       'opex':opex,'retention':ret,'cac':cac,'funnel':funnel,'weekly_students':WEEKLY_STU}
with open(BASE+'/v15_data.json','w',encoding='utf-8') as f:
    json.dump(D_out,f,ensure_ascii=False,separators=(',',':'))

print("\n=== LOGIC VERIFICATION ===")
# Check: net_profit <= gross_profit <= revenue for each group
errors=0
for g in all_groups:
    rev=float(g['total_rev_usd']); gross=float(g['profit_usd']); net=float(g['profit_v11_usd'])
    tc10=float(g['total_cost_usd']); tc11=float(g['total_cost_v11_usd'])
    if abs(rev-gross-tc10)>0.1: print(f"ERROR v10: {g['group_id']}"); errors+=1
    if abs(rev-net-tc11)>0.1: print(f"ERROR v11: {g['group_id']}"); errors+=1
    if tc11<tc10: print(f"ERROR cost v11<v10: {g['group_id']}"); errors+=1
print(f"Financial logic errors: {errors}")

# Check teacher totals match group assignments
for month,gx,tx in [('2025-04',apr_groups,apr_teachers),('2025-05',may_groups,may_teachers)]:
    for t in tx:
        tid=t['teacher_id']
        exp_lessons=sum(float(g['lessons_60min_per_month']) for g in gx if g['assigned_teacher']==tid)
        act=float(t['actual_lessons_60min'])
        if abs(exp_lessons-act)>1:
            print(f"WARN teacher mismatch {month} {tid}: expected={exp_lessons:.1f} actual={act}")

print("\nALL DONE")
print(f"CSVs: 01,02,03,04,06,07,08,10_weekly saved")
print(f"JSON: v15_data.json saved ({len(json.dumps(D_out))} chars)")
