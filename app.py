import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Workplace Operations Dashboard", page_icon="🏢", layout="wide")
st.title("🏢 Workplace Operations Dashboard")
st.caption("MoveInSync TAM / Implementation Intern assessment demo")
st.info("Demo data only. Replace illustrative inputs with validated operational data before making real decisions.")

st.sidebar.header("Planning assumptions")
employees = st.sidebar.number_input("Total employees", 1, 100000, 2000, 50)
office_days = st.sidebar.slider("Office days per employee / week", 1, 5, 3)
working_days = st.sidebar.slider("Working days per week", 1, 7, 5)
buffer_pct = st.sidebar.slider("Planning buffer above average (%)", 0, 50, 15)
st.sidebar.caption("Buffer is a planning assumption, not a guaranteed peak-capacity requirement.")

st.sidebar.subheader("Employee split by office")
names = ["Office A", "Office B", "Office C"]
defaults = [800, 650, 550]
headcounts = [st.sidebar.number_input(f"{n} employees", 0, employees, min(defaults[i], employees), 25, key=f"hc{i}") for i,n in enumerate(names)]
if sum(headcounts) != employees:
    st.sidebar.warning(f"Office split totals {sum(headcounts):,}, not {employees:,}. Update the split to match total headcount.")

weekly_days = employees * office_days
avg_daily = weekly_days / working_days
recommended = round(avg_daily * (1 + buffer_pct / 100))

st.header("1. Seating capacity")
a,b,c,d = st.columns(4)
a.metric("Total employees", f"{employees:,}")
b.metric("Weekly employee-days", f"{weekly_days:,}")
c.metric("Average daily attendance", f"{avg_daily:,.0f}")
d.metric("Maximum simultaneous seats", f"{employees:,}")
a,b,c = st.columns(3)
a.metric("Theoretical minimum seats", f"{avg_daily:,.0f}")
b.metric("Illustrative starting capacity", f"{recommended:,}")
c.metric("Planning buffer", f"{buffer_pct}%")
st.markdown("The theoretical minimum assumes perfectly balanced attendance across the working week. Maximum capacity assumes everyone could attend together. Final capacity should be based on actual peak attendance.")

office_rows=[]
for n,h in zip(names,headcounts):
    avg=h*office_days/working_days
    office_rows.append({"Office":n,"Employees":h,"Weekly employee-days":h*office_days,"Average daily attendance":round(avg,1),"Illustrative seats (+ buffer)":round(avg*(1+buffer_pct/100)),"Maximum simultaneous seats":h})
office_df=pd.DataFrame(office_rows)
st.subheader("Office-by-office estimate")
st.dataframe(office_df, use_container_width=True, hide_index=True)
office_fig=px.bar(office_df.melt(id_vars="Office",value_vars=["Average daily attendance","Illustrative seats (+ buffer)","Maximum simultaneous seats"],var_name="Measure",value_name="Seats"),x="Office",y="Seats",color="Measure",barmode="group",title="Estimated seating demand by office")
st.plotly_chart(office_fig,use_container_width=True)

st.divider()
st.header("2. Weekday demand and seat utilization")
st.caption("Default values are illustrative and editable.")
weekdays=["Monday","Tuesday","Wednesday","Thursday","Friday"]
weekday_df=pd.DataFrame({"Weekday":weekdays,"Expected attendance":[950,1350,1450,1300,950],"Available seats":[recommended]*5})
with st.expander("Edit weekday attendance and capacity"):
    weekday_df=st.data_editor(weekday_df,use_container_width=True,hide_index=True,num_rows="fixed",column_config={"Weekday":st.column_config.TextColumn(disabled=True),"Expected attendance":st.column_config.NumberColumn(min_value=0,step=25),"Available seats":st.column_config.NumberColumn(min_value=0,step=25)})
weekday_df["Seat utilization (%)"]=(weekday_df["Expected attendance"]/weekday_df["Available seats"].replace(0,pd.NA)*100).fillna(0).round(1)
st.plotly_chart(px.bar(weekday_df,x="Weekday",y="Expected attendance",text="Expected attendance",title="Expected attendance by weekday"),use_container_width=True)
util=px.line(weekday_df,x="Weekday",y="Seat utilization (%)",markers=True,title="Seat utilization by weekday")
util.add_hline(y=90,line_dash="dash",annotation_text="Illustrative 90% guardrail")
st.plotly_chart(util,use_container_width=True)
peak=weekday_df.loc[weekday_df["Seat utilization (%)"].idxmax()]
if peak["Seat utilization (%)"]>100:
    st.error(f"Capacity risk: demand exceeds seats on {peak['Weekday']} ({peak['Seat utilization (%)']:.1f}%).")
elif peak["Seat utilization (%)"]>=90:
    st.warning(f"Peak utilization is {peak['Seat utilization (%)']:.1f}% on {peak['Weekday']}. Validate capacity and booking rules.")
else:
    st.success(f"Highest estimated utilization is {peak['Seat utilization (%)']:.1f}% on {peak['Weekday']}. Validate with actual check-in data.")

st.divider()
st.header("3. Booking and facilities KPIs")
c1,c2,c3,c4=st.columns(4)
bookings=c1.number_input("Desk bookings",0,1000000,1200,50)
no_shows=c2.number_input("Bookings with no check-in",0,1000000,96,10)
requests=c3.number_input("Facilities requests",0,1000000,200,10)
on_time=c4.number_input("Requests resolved within SLA",0,1000000,190,10)
c1,c2,c3,c4=st.columns(4)
maint_due=c1.number_input("Maintenance tasks due",0,1000000,100,10)
maint_done=c2.number_input("Maintenance completed on time",0,1000000,98,5)
satisfaction=c3.slider("Employee satisfaction (/5)",1.0,5.0,4.2,0.1)
monthly_cost=c4.number_input("Monthly facilities cost (₹)",0,1000000000,12000000,100000)
no_show_rate=no_shows/bookings*100 if bookings else 0
sla_rate=on_time/requests*100 if requests else 0
maint_rate=maint_done/maint_due*100 if maint_due else 0
seat_days=int(weekday_df["Expected attendance"].sum())
cost_per=monthly_cost/seat_days if seat_days else 0
k1,k2,k3,k4=st.columns(4)
k1.metric("Booking no-show rate",f"{no_show_rate:.1f}%")
k2.metric("Requests resolved within SLA",f"{sla_rate:.1f}%")
k3.metric("Preventive maintenance on time",f"{maint_rate:.1f}%")
k4.metric("Employee satisfaction",f"{satisfaction:.1f}/5")
k1,k2=st.columns(2)
k1.metric("Estimated cost per occupied seat-day",f"₹{cost_per:,.0f}",help="For operational use, make sure cost and attendance time periods match.")
k2.metric("Estimated occupied seat-days in sample week",f"{seat_days:,}")
scorecard=pd.DataFrame([
{"KPI":"Peak seat utilization","Current":f"{peak['Seat utilization (%)']:.1f}%","Illustrative target":"Below 90%","Potential action":"Review peak-day capacity and team schedules"},
{"KPI":"Booking no-show rate","Current":f"{no_show_rate:.1f}%","Illustrative target":"Below 10%","Potential action":"Improve reminders and cancellation rules"},
{"KPI":"SLA compliance","Current":f"{sla_rate:.1f}%","Illustrative target":"At least 95%","Potential action":"Review staffing, request categories and escalation"},
{"KPI":"Preventive maintenance","Current":f"{maint_rate:.1f}%","Illustrative target":"At least 98%","Potential action":"Prioritize critical assets and overdue tasks"},
{"KPI":"Employee satisfaction","Current":f"{satisfaction:.1f}/5","Illustrative target":"At least 4.2/5","Potential action":"Analyze feedback and fix recurring issues"},
])
st.subheader("KPI scorecard")
st.dataframe(scorecard,use_container_width=True,hide_index=True)

st.divider()
st.header("4. Implementation plan")
st.dataframe(pd.DataFrame([
{"Phase":"Discover","Activities":"Confirm headcount by office, schedules, desk inventory, holidays and employee needs."},
{"Phase":"Validate data","Activities":"Compare bookings with check-ins; check data quality, privacy and KPI definitions."},
{"Phase":"Configure","Activities":"Set up locations, desks, employee groups, booking rules and permissions."},
{"Phase":"Pilot","Activities":"Test in one office/team and compare KPIs with a baseline."},
{"Phase":"Optimize","Activities":"Adjust capacity and scheduling from observed peaks, then scale to other offices."},
]),use_container_width=True,hide_index=True)
st.caption("Independent portfolio demo; not an official WorkInSync product or connected company system. All sample attendance, KPI and cost figures are illustrative.")
