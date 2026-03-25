frappe.listview_settings["Project Budget"] = {

     filters: [
        ['is_active_revision']
    ],

    formatters: {
        budget_utilization_percentage(value) {

            // if (!value) return "";

            let color = "green";
            let percent = Math.round(value);

            if (percent > 100) color = "red";
            else if (percent >= 70) color = "orange";

            return `
                <div style="width:120px;background:#eee;border-radius:4px;">
                    <div style="
                        width:${percent}%;
                        background:${color};
                        color:white;
                        text-align:center;
                        font-size:10px;
                        border-radius:4px;"
                        title="Budget Utilization: ${percent}%">
                        ${percent}%
                    </div>
                </div>
            `;
        },
        budget_status(value) {

            if (value === "Over Budget") {
                return `<span style="color:red; font-weight:bold;">${value}</span>`;
            }

            if (value === "Under Budget") {
                return `<span style="color:green; font-weight:bold;">${value}</span>`;
            }

            if (value === "On Budget") {
                return `<span style="color:orange; font-weight:bold;">${value}</span>`;
            }
        }
    }
};