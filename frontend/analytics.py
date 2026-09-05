import plotly.express as px

def sales_chart(frame):
    return px.line(frame, x="date", y="total_amount", title="Daily sales")
