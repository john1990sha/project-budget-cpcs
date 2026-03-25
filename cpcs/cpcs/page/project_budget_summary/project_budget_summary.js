frappe.pages['project-budget-summary'].on_page_load = function(wrapper) {

    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Project Budget Summary',
        single_column: true
    });

    // ✅ FILTER
    let project = page.add_field({
        label: 'Project',
        fieldname: 'project',
        fieldtype: 'Link',
        options: 'Project'
    });

    // ✅ CONTAINER
    let container = $('<div id="report-container"></div>');
    page.body.append(container);

    // ✅ GET REPORT BUTTON
    page.add_inner_button('Get Report', function() {

        let project_value = project.get_value();

        if (!project_value) {
            frappe.msgprint("Please select a Project");
            return;
        }

        load_report(project_value);

    });

    // ✅ PRINT BUTTON
    page.add_inner_button('Print', function() {
        window.print();
    });

    // function load all project
    load_report();

};


function render_report(data) {

    let html = frappe.render_template("project_budget_summary", {
        columns: data.columns || [],
        rows: data.result || [],
        project: data.filters?.project || ""
    });

    $('#report-container').html(html);
}

// load all projects
function load_report(project_value = null) {

    frappe.call({
        method: "cpcs.cpcs.page.project_budget_summary.project_budget_summary.get_project_budget_summary",
        args: {
            filters: {
                project: project_value || ""
            }
        },
        callback: function(r) {

            console.log("Full Response:", r);

            if (r.message && r.message.result) {

                render_report(r.message);

            } else {
                frappe.msgprint("No data found");
                $('#report-container').html("<p>No data available</p>");
            }
        }
    });
}