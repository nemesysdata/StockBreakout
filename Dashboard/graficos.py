import altair as alt
ANNOTATION_COLOR = "white"
###############################################################################
def candle_stick(data, data_breakout):
    """
    Cria um gráfico de candlestick
    """
    open_close_color = alt.condition(
        "datum.openv <= datum.closev",
        alt.value("#06982d"),
        alt.value("#ae1325")
    )

    base = alt.Chart(data).encode(
        alt.X('datetime:T')
            .axis(format='%d/%m/%y', labelAngle=-45, grid=True, gridDash=[2,5], labelAlign='center')
            .title(''),
        color=open_close_color
    )

    rule = base.mark_rule().encode(
        alt.Y('lowv:Q')
            .title('Price')
            .axis(grid=True, gridDash=[2,5])
            .scale(zero=False),
        alt.Y2('highv:Q'),
        color=alt.value("#707070")
    )

    bar = base.mark_bar().encode(
        alt.Y('openv:Q'),
        alt.Y2('closev:Q')
    )

    xrule = (alt.Chart().mark_rule(color=ANNOTATION_COLOR, strokeWidth=1, strokeDash=[2,5])
            .encode(x=alt.datum(alt.DateTime(year=data_breakout.year, month=data_breakout.month, date=data_breakout.day)))
    )

    chart = rule + bar + xrule
    chart.title = "Evolução do Valor da Ação"
    return chart
###############################################################################
def o_c_analysis(breakouts, data_breakout):
    hi_low_color = alt.condition(
        "datum.o_to_c > 0",
        alt.value("#06982d"),
        alt.value("#ae1325")
    )

    base = alt.Chart(breakouts).encode(
        alt.X('datetime:T')
            .axis(format='%d/%m/%y', labelAngle=-45, grid=True, gridDash=[2,5], labelAlign='center')
            .title(''),
        color=hi_low_color
    )
    bar1 = base.mark_bar().encode(
        alt.Y('o_to_c:Q')
            .title('OC vs Max Últimos 10 dias')
            .axis(grid=True, gridDash=[2,5])
            .scale(zero=False),
    )

    line1 = base.mark_line().encode(
        alt.Y('maxoc_prev10d:Q')
            .scale(zero=False),
            color=alt.value("#0000AA")
    )

    bar = bar1 + line1

    xrule = (alt.Chart().mark_rule(color=ANNOTATION_COLOR, strokeWidth=1, strokeDash=[2,5])
        .encode(x=alt.datum(alt.DateTime(year=data_breakout.year, month=data_breakout.month, date=data_breakout.day)))
    )

    chart = bar + xrule

    chart.title = "O - C deve ser a maior nos últimos 10 dias"
    return chart
###############################################################################
def perc_analysis1(breakouts, data_breakout):
    base = alt.Chart(breakouts).encode(
        alt.X('datetime:T')
            .axis(format='%d/%m/%y', labelAngle=-45, grid=True, gridDash=[2,5], labelAlign='center')
            .title(''),
        color=alt.value("#00AA00")
    )

    line1 = base.mark_line().encode(
        alt.Y('oc_perc_20d_mean:Q')
        .title('% Diferença entre Open e Close')
        .axis(grid=True, gridDash=[2,5])
        .scale(domain=(-200, 200), clamp=True)
    )

    bar = line1 + line1
    
    xrule = (alt.Chart().mark_rule(color=ANNOTATION_COLOR, strokeWidth=1, strokeDash=[2,5])
        .encode(x=alt.datum(alt.DateTime(year=data_breakout.year, month=data_breakout.month, date=data_breakout.day)))
    )

    yrule = (
        alt.Chart().mark_rule(color=ANNOTATION_COLOR, strokeDash=[2, 5], size=2).encode(y=alt.datum(100))
    )    

    chart = bar + xrule + yrule
    chart.title = "Variação O - C deve ser 100% > média dos últimos 20 dias"    
    return chart
###############################################################################
def perc_analysis2(breakouts, data_breakout):
    base = alt.Chart(breakouts).encode(
        alt.X('datetime:T')
            .axis(format='%d/%m/%y', labelAngle=-45)
            .title(''),
        color=alt.value("#00AA00")
    )

    line1 = base.mark_line().encode(
        alt.Y('vol_perc_20d_mean:Q')
            .title('Diferença entre Open e Close')
            .scale(zero=False)            
    )

    bar = line1 + line1

    xrule = (alt.Chart().mark_rule(color=ANNOTATION_COLOR, strokeWidth=1, strokeDash=[2,5])
        .encode(x=alt.datum(alt.DateTime(year=data_breakout.year, month=data_breakout.month, date=data_breakout.day)))
    )

    yrule = (
        alt.Chart().mark_rule(color=ANNOTATION_COLOR, strokeDash=[2, 5], size=2).encode(y=alt.datum(50))
    )    

    chart = bar + xrule + yrule
    chart.title = "Variação Volume deve ser 50% > média dos últimos 20 dias"
    return chart
###############################################################################
def value_stocks(data):
    min = data['closev'].min()
    max = data['closev'].max()

    chart = alt.Chart(data).mark_line().encode(
        alt.X('datetime:T', axis=alt.Axis(labels=False), title=''),
        alt.Y('closev:Q').scale(domain=(min,max)).title(''),
    )

    chart.height = 100

    return chart