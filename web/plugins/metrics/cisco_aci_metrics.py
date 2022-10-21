from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info

metric_info["health"] = {
    "title": _("Health score"),
    "unit": "count",
    "color": "34/a",
}

metric_info["dom_rx_power"] = {
    "title": _("DOM RX Power"),
    "unit": "dbm",
    "color": "31/a",
}

metric_info["dom_tx_power"] = {
    "title": _("DOM TX Power"),
    "unit": "dbm",
    "color": "26/a",
}

metric_info["fcs_errors"] = {
    "title": _("FCS errors"),
    "unit": "count",
    "color": "14/a",
}

metric_info["crc_errors"] = {
    "title": _("CRC errors"),
    "unit": "count",
    "color": "16/a",
}

metric_info["stomped_crc_errors"] = {
    "title": _("stomped CRC errors"),
    "unit": "count",
    "color": "21/a",
}

metric_info["bgp_conn_attempts"] = {
    "title": _("BGP connection attempts"),
    "unit": "count",
    "color": "46/a",
}

metric_info["bgp_conn_drop"] = {
    "title": _("BGP connection drops"),
    "unit": "count",
    "color": "45/a",
}

metric_info["bgp_conn_est"] = {
    "title": _("BGP connection establishments"),
    "unit": "count",
    "color": "44/a",
}
