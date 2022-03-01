from flask import render_template


def render_integrations(context, slot, payload):
    from ...shared.connectors.auth import SessionProject
    project_id = SessionProject.get()
    # results = context.rpc_manager.call.integrations_get_project_integrations(payload['id'])
    results = context.rpc_manager.call.integrations_get_project_integrations(project_id)

    payload['existing_integrations'] = results
    payload['integrations_section_list'] = context.rpc_manager.call.integrations_section_list()

    return render_template(
        'integrations:integrations_list.html',
        config=payload
    )


def render_default_add_button(context, slot, payload):
    return render_template(
        'integrations:default_add_button.html',
        config=payload
    )
