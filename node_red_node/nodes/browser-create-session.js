const axios = require('axios');
function registerCreateSessionNode(RED) {
    function CreateSessionNode(config) {
        RED.nodes.createNode(this, config);
        this.on('input', async (msg) => {
            const apiUrl = (msg.apiUrl || process.env.BROWSER_API_URL || "http://localhost:5000/browser/open");
            let payload = {};
            if (msg.payload && typeof msg.payload === 'object' && !Array.isArray(msg.payload)) {
                payload = msg.payload;
            }
            try {
                const response = await axios.post(apiUrl, payload);
                msg.session_id = response.data.session_id;
                this.send(msg);
            } catch (err) {
                let detail = '';
                if (err.response) {
                    detail = `Status: ${err.response.status}, Data: ${JSON.stringify(err.response.data)}`;
                } else if (err.request) {
                    detail = 'No response received from server.';
                } else {
                    detail = err.message;
                }
                this.error("Failed to create session: " + detail, msg);
            }
        });
    }
    RED.nodes.registerType("browser-create-session", CreateSessionNode);
}

module.exports = registerCreateSessionNode;
