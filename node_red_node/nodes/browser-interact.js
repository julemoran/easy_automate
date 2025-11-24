const axios = require('axios');
function registerInteractNode(RED) {
    function InteractNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', async (msg) => {
            // Copy config values to msg if not already set
            const pageId = msg.page_id || config.page_id;
            const alias = msg.selector_alias || config.selector_alias;
            const op = msg.interaction || config.interaction || "click"; // click, set-value, get-value
            const value = (msg.value !== undefined) ? msg.value : config.value;
            const sessionId = msg.session_id;
            console.log("InteractNode received msg:", msg);
            if (!sessionId || !pageId || !alias) {
                this.error("Missing session_id, page_id, or selector_alias in msg for interact", msg);
                return;
            }
            let apiUrl, req;
            try {
                if (op === "click") {
                    apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/click`);
                    req = axios.post(apiUrl, { page_id: pageId, selector_alias: alias });
                } else if (op === "set-value") {
                    if (value === undefined) throw new Error("Missing value for set-value");
                    apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/set-value`);
                    req = axios.post(apiUrl, { page_id: pageId, selector_alias: alias, value });
                } else if (op === "get-value") {
                    apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/get-value`);
                    req = axios.post(apiUrl, { page_id: pageId, selector_alias: alias });
                } else {
                    throw new Error("Unknown interaction op: " + op);
                }
                const response = await req;
                if (op === "get-value") {
                    msg.value = response.data.value;
                } else {
                    msg.success = true;
                }
                this.send(msg);
            } catch (err) {
                this.error(`Failed to ${op}: ` + (err.response?.data?.error || err.message), msg);
            }
        });
    }
    RED.nodes.registerType("browser-interact", InteractNode);
}

module.exports = registerInteractNode;
