from app import app, facade
from dash import Input, Output, callback, no_update



@callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    return facade.current_template.tabs_dict[active_tab]
