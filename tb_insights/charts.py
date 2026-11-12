from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .data import CLUSTER_COLORS, WHO_REGION_NAMES, WHO_REGION_SHORT_NAMES, cluster_display_name

NAVY = "#142D4E"
BLUE = "#4F78D8"
TEAL = "#149C91"
ORANGE = "#E58A4E"
PURPLE = "#8C72CC"
MUTED = "#718096"
GRID = "#E8EDF3"

CHART_CONFIG = {
    "displayModeBar": "hover",
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def base_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=22, r=22, t=34, b=22),
        font=dict(family="DM Sans, Arial, sans-serif", color=NAVY, size=12),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        hoverlabel=dict(bgcolor=NAVY, font_color="white", bordercolor=NAVY),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID, ticks="outside", tickcolor=GRID)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def trend_figure(summary: pd.DataFrame, metric: str, title: str, color: str, suffix: str) -> go.Figure:
    fig = go.Figure()
    if not summary.empty:
        coverage_col = "countries_inc" if metric == "inc_rate" else "countries_mort"
        coverage = summary[coverage_col].to_numpy() if coverage_col in summary.columns else np.full(len(summary), np.nan)
        fig.add_trace(go.Scatter(
            x=summary["year"], y=summary[metric], mode="lines+markers", name=title,
            line=dict(color=color, width=3), marker=dict(size=5, color=color),
            customdata=coverage,
            connectgaps=False,
            hovertemplate=("Năm %{x}<br>" + title + ": %{y:,.1f}" + suffix
                           + "<br>Số quốc gia/vùng lãnh thổ có dữ liệu: %{customdata:.0f}<extra></extra>"),
        ))
    else:
        fig.add_annotation(text="Không có dữ liệu cho bộ lọc đang chọn", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
    fig.update_layout(title=dict(text=title, x=0.02, font=dict(size=14)), showlegend=False)
    fig.update_xaxes(title="Năm", dtick=4, tickformat="d")
    fig.update_yaxes(title=suffix.strip())
    return base_layout(fig, 340)


def bar_figure(data: pd.DataFrame, metric: str, label: str, color: str = BLUE, height: int = 380) -> go.Figure:
    d = data.dropna(subset=[metric]).sort_values(metric, ascending=True).copy()
    if d.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu phù hợp", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
        return base_layout(fig, height)
    fig = px.bar(
        d, x=metric, y="country", orientation="h", text=metric,
        color_discrete_sequence=[color],
        hover_data={"iso3": True, metric: ":,.1f"},
    )
    fig.update_traces(
        texttemplate="%{text:,.1f}", textposition="outside", cliponaxis=False,
        marker_line_width=0,
        hovertemplate="%{y}<br>" + label + ": %{x:,.1f}<extra></extra>",
    )
    fig.update_layout(title=dict(text=label, x=0.02, font=dict(size=14)), showlegend=False)
    fig.update_xaxes(title=label)
    fig.update_yaxes(title="", automargin=True)
    return base_layout(fig, height)


def choropleth_figure(data: pd.DataFrame, metric: str = "e_inc_100k") -> go.Figure:
    d = data.dropna(subset=[metric, "iso3"]).copy()
    fig = px.choropleth(
        d, locations="iso3", color=metric, hover_name="country",
        hover_data={"iso3": True, metric: ":,.1f"},
        color_continuous_scale=[[0, "#E8F1FA"], [0.45, "#79A7D8"], [1, "#17436B"]],
        labels={metric: "Ca/100.000 dân"},
    )
    fig.update_geos(
        showframe=False, showcoastlines=True, coastlinecolor="#CFD8E3",
        showcountries=True, countrycolor="#DDE4EC", showland=True, landcolor="#F0F3F7",
        showocean=True, oceancolor="#FAFCFE", projection_type="natural earth",
    )
    fig.update_layout(
        title=dict(text="Phân bố tỷ lệ mắc theo quốc gia", x=0.02, font=dict(size=14)),
        coloraxis_colorbar=dict(title="Ca/100.000", thickness=12, len=0.7),
    )
    return base_layout(fig, 470)


def country_trend_figure(
    data: pd.DataFrame, metric: str, low: str | None, high: str | None,
    title: str, color: str,
) -> go.Figure:
    d = data.sort_values("year").dropna(subset=[metric])
    fig = go.Figure()
    if low in d.columns and high in d.columns:
        band = d.dropna(subset=[low, high])
        if not band.empty:
            fig.add_trace(go.Scatter(
                x=band["year"], y=band[high], mode="lines", line=dict(width=0),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=band["year"], y=band[low], mode="lines", line=dict(width=0),
                fill="tonexty", fillcolor="rgba(79,120,216,.12)",
                name="Khoảng bất định (ước tính thấp–cao)", hoverinfo="skip",
            ))
    if not d.empty:
        fig.add_trace(go.Scatter(
            x=d["year"], y=d[metric], mode="lines+markers", name=title,
            line=dict(color=color, width=3), marker=dict(size=5),
            hovertemplate="Năm %{x}<br>" + title + ": %{y:,.1f}<extra></extra>",
        ))
    else:
        fig.add_annotation(text="Không có dữ liệu cho quốc gia này", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
    fig.update_layout(title=dict(text=title, x=.02, font=dict(size=14)), showlegend=False)
    fig.update_xaxes(title="Năm", dtick=4, tickformat="d")
    fig.update_yaxes(title="Ca/100.000 dân")
    return base_layout(fig, 340)


def clustering_scatter(cluster_data: pd.DataFrame) -> go.Figure:
    """Country-level scatter; axes are log-transformed for readability."""
    d = cluster_data.copy()
    if d.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có quốc gia phù hợp với bộ lọc", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
        return base_layout(fig, 470)

    d["incidence_log1p"] = np.log1p(d["e_inc_100k"].clip(lower=0))
    d["mortality_log1p"] = np.log1p(d["e_mort_100k"].clip(lower=0))
    d["cluster_label"] = d["cluster_name_vi"].map(cluster_display_name)
    size = np.log10(d["e_pop_num"].clip(lower=1))
    d["population_size"] = 9 + (size - size.min()) / max(size.max() - size.min(), 1e-9) * 16

    order = [cluster_display_name(k) for k in CLUSTER_COLORS]
    color_map = {cluster_display_name(k): v for k, v in CLUSTER_COLORS.items()}
    fig = px.scatter(
        d, x="incidence_log1p", y="mortality_log1p", color="cluster_label",
        size="population_size", size_max=25, hover_name="country",
        hover_data={
            "iso3": True, "e_inc_100k": ":,.1f", "e_mort_100k": ":,.1f",
            "c_cdr": ":,.1f", "g_whoregion": True,
            "population_size": False, "incidence_log1p": False, "mortality_log1p": False,
        },
        color_discrete_map=color_map,
        category_orders={"cluster_label": order},
        labels={"cluster_label": "Nhóm quốc gia"},
    )
    vn = d[d["iso3"].eq("VNM")]
    if not vn.empty:
        fig.add_trace(go.Scatter(
            x=vn["incidence_log1p"], y=vn["mortality_log1p"], mode="markers+text",
            name="Việt Nam", text=["Việt Nam"], textposition="top right",
            marker=dict(symbol="star", size=19, color=NAVY, line=dict(color="white", width=1.5)),
            hovertemplate=("Việt Nam<br>Tỷ suất mắc mới: %{customdata[0]:,.1f}/100.000 dân"
                           "<br>Tỷ suất tử vong: %{customdata[1]:,.1f}/100.000 dân<extra></extra>"),
            customdata=vn[["e_inc_100k", "e_mort_100k"]].to_numpy(),
        ))

    # The section heading is rendered by Streamlit outside the chart. Do not
    # add another Plotly title; reserve top space for a clean legend instead.
    fig = base_layout(fig, 470)
    fig.update_layout(
        title=None, legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=68, r=18, t=58, b=58),
    )
    fig.update_xaxes(title="Tỷ suất mắc mới (thang logarit)", automargin=True)
    fig.update_yaxes(title="Tỷ suất tử vong (thang logarit)", automargin=True)
    return fig


def cluster_region_figure(cluster_data: pd.DataFrame) -> go.Figure:
    """Horizontal stacked bars with localized region names and a clean legend."""
    if cluster_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu phù hợp với bộ lọc", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
        return base_layout(fig, 350)

    counts = (
        cluster_data.groupby(["g_whoregion", "cluster_name_vi"], dropna=False)["iso3"]
        .nunique().reset_index(name="countries")
    )
    counts["region"] = counts["g_whoregion"].map(WHO_REGION_SHORT_NAMES).fillna(counts["g_whoregion"])
    counts["cluster_label"] = counts["cluster_name_vi"].map(cluster_display_name)
    region_order = (
        counts.groupby("region")["countries"].sum().sort_values(ascending=True).index.tolist()
    )
    order = [cluster_display_name(k) for k in CLUSTER_COLORS]
    color_map = {cluster_display_name(k): v for k, v in CLUSTER_COLORS.items()}
    fig = px.bar(
        counts, x="countries", y="region", orientation="h", color="cluster_label",
        barmode="stack", category_orders={"region": region_order, "cluster_label": order},
        color_discrete_map=color_map,
        labels={"region": "Khu vực WHO", "countries": "Số quốc gia", "cluster_label": "Nhóm quốc gia"},
        hover_data={"g_whoregion": False, "countries": True},
    )
    fig.update_traces(
        hovertemplate="%{y}<br>Nhóm: %{fullData.name}<br>Số quốc gia: %{x}<extra></extra>",
        marker_line_width=0,
    )
    fig = base_layout(fig, 390)
    fig.update_layout(
        title=None, legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=18, r=24, t=54, b=48),
        bargap=.28,
    )
    fig.update_xaxes(title="Số quốc gia/vùng lãnh thổ", showgrid=True, gridcolor=GRID, rangemode="tozero")
    fig.update_yaxes(title="", automargin=True)
    return fig


def kmeans_model_selection_figure(metrics: pd.DataFrame) -> go.Figure:
    """Show silhouette scores over K and preprocessing scenarios; highlight the chosen setting."""
    if metrics.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có bảng so sánh mô hình", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
        return base_layout(fig, 390)
    d = metrics.copy()
    label_col = "preprocessing_vi" if "preprocessing_vi" in d.columns else "preprocessing"
    fig = px.line(
        d, x="k", y="silhouette", color=label_col, markers=True,
        labels={"k": "Số nhóm K", "silhouette": "Silhouette Score", label_col: "Cách chuẩn hóa"},
        color_discrete_sequence=[BLUE, PURPLE, TEAL],
    )
    selected = d[d.get("is_selected", False).astype(bool)] if "is_selected" in d.columns else pd.DataFrame()
    if not selected.empty:
        fig.add_trace(go.Scatter(
            x=selected["k"], y=selected["silhouette"], mode="markers",
            name="Cấu hình được chọn", marker=dict(symbol="star", size=17, color=ORANGE, line=dict(color=NAVY, width=1)),
            hovertemplate="Cấu hình được chọn<br>K=%{x}<br>Silhouette=%{y:.3f}<extra></extra>",
        ))
    fig.update_layout(title=None, legend_title_text="", margin=dict(l=48, r=20, t=35, b=48))
    fig.update_xaxes(dtick=1, tickmode="linear", range=[1.8, 8.2])
    fig.update_yaxes(title="Silhouette Score", rangemode="tozero", showgrid=True, gridcolor=GRID)
    return base_layout(fig, 390)


def cluster_region_share_figure(cluster_data: pd.DataFrame) -> go.Figure:
    """100% stacked regional cluster composition; complements absolute counts."""
    if cluster_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu phù hợp với bộ lọc", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
        return base_layout(fig, 350)
    counts = (
        cluster_data.groupby(["g_whoregion", "cluster_name_vi"], dropna=False)["iso3"]
        .nunique().reset_index(name="countries")
    )
    counts["region"] = counts["g_whoregion"].map(WHO_REGION_SHORT_NAMES).fillna(counts["g_whoregion"])
    counts["share_pct"] = counts["countries"] / counts.groupby("region")["countries"].transform("sum") * 100
    counts["cluster_label"] = counts["cluster_name_vi"].map(cluster_display_name)
    region_order = counts.groupby("region")["countries"].sum().sort_values(ascending=True).index.tolist()
    order = [cluster_display_name(k) for k in CLUSTER_COLORS]
    color_map = {cluster_display_name(k): v for k, v in CLUSTER_COLORS.items()}
    fig = px.bar(
        counts, x="share_pct", y="region", orientation="h", color="cluster_label",
        barmode="stack", category_orders={"region": region_order, "cluster_label": order},
        color_discrete_map=color_map,
        labels={"region": "Khu vực WHO", "share_pct": "Tỷ trọng trong khu vực (%)", "cluster_label": "Nhóm quốc gia"},
        hover_data={"countries": True, "share_pct": ":.1f", "g_whoregion": False},
    )
    fig.update_traces(hovertemplate="%{y}<br>Nhóm: %{fullData.name}<br>Tỷ trọng: %{x:.1f}%<br>Số quốc gia/vùng lãnh thổ: %{customdata[0]}<extra></extra>")
    fig.update_layout(title=None, legend_title_text="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), margin=dict(l=18, r=24, t=54, b=48), bargap=.28)
    fig.update_xaxes(title="Tỷ trọng trong từng khu vực (%)", range=[0, 100], ticksuffix="%", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title="", automargin=True)
    return base_layout(fig, 390)


def cluster_profile_comparison(
    profile: pd.DataFrame, reference_profile: pd.DataFrame | None = None
) -> go.Figure:
    """Compare cluster medians with per-indicator normalization (max = 100%)."""
    metrics = ["incidence_median", "mortality_median", "cdr_median"]
    metric_labels = [
        "Tỷ suất mắc mới",
        "Tỷ suất tử vong",
        "Tỷ lệ phát hiện ca bệnh",
    ]
    units = ["ca/100.000 dân", "ca/100.000 dân", "%"]
    fig = go.Figure()
    if profile.empty:
        fig.add_annotation(text="Không có nhóm phù hợp với bộ lọc", showarrow=False,
                           xref="paper", yref="paper", x=.5, y=.5, font=dict(color=MUTED))
        return base_layout(fig, 360)

    reference = reference_profile if reference_profile is not None and not reference_profile.empty else profile
    max_vals = reference[metrics].max().replace(0, np.nan)
    y_positions = metric_labels
    for _, row in profile.iterrows():
        raw_values = [row[m] for m in metrics]
        normalized = [
            (float(row[m]) / float(max_vals[m]) * 100)
            if pd.notna(max_vals[m]) and pd.notna(row[m]) else 0.0
            for m in metrics
        ]
        custom = [[raw, unit] for raw, unit in zip(raw_values, units)]
        display_name = cluster_display_name(row["cluster_name_vi"])
        fig.add_trace(go.Bar(
            x=normalized, y=y_positions, orientation="h", name=display_name,
            marker_color=CLUSTER_COLORS.get(str(row["cluster_name_vi"]), BLUE),
            text=[f"{v:.0f}%" for v in normalized], textposition="outside", cliponaxis=False,
            customdata=custom,
            hovertemplate=("%{y}<br>Giá trị thực tế: %{customdata[0]:,.1f} %{customdata[1]}"
                           "<br>So với nhóm có trung vị cao nhất: %{x:.1f}%<extra></extra>"),
        ))

    fig = base_layout(fig, 390)
    fig.update_layout(
        title=None, barmode="group", legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=12, r=48, t=54, b=52),
        bargap=.35, bargroupgap=.12,
    )
    fig.update_xaxes(
        title="So với nhóm có trung vị cao nhất của từng chỉ số (%)",
        range=[0, 115], showgrid=True, gridcolor=GRID, ticksuffix="%",
    )
    fig.update_yaxes(title="", categoryorder="array", categoryarray=metric_labels[::-1], automargin=True)
    return fig
