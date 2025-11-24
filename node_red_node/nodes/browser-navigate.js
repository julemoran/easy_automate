const axios = require('axios');
function registerNavigateNode(RED) {
    function NavigateNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', async (msg) => {
            const sessionId = msg.session_id;
            // Use msg.page_id if present, otherwise use config.page_id
            const pageId = msg.page_id || config.page_id;
            if (!sessionId || !pageId) {
                this.error("Missing session_id or page_id in msg for navigate", msg);
                return;
            }
            const apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || `http://localhost:5000/browser/${sessionId}/navigate`);
            try {
                await axios.post(apiUrl, { page_id: pageId });
                msg.navigated = true;
                msg.page_id = pageId; // propagate for downstream nodes
                this.send(msg);
            } catch (err) {
                this.error("Failed to navigate: " + (err.response?.data?.error || err.message), msg);
            }
        });
    }
    RED.nodes.registerType("browser-navigate", NavigateNode);
}

module.exports = registerNavigateNode;
