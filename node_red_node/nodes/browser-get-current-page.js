const axios = require('axios');

module.exports = function (RED) {
    function BrowserGetCurrentPageNode(config) {
        RED.nodes.createNode(this, config);
        var node = this;
        node.session_id = config.session_id;

        node.on('input', async function (msg, send, done) {
            const session_id = node.session_id || msg.session_id;
            if (!session_id) {
                node.error('Session ID is required', msg);
                if (done) done();
                return;
            }
            const baseUrl = msg.baseUrl || node.credentials?.baseUrl || 'http://localhost:5000/browser';
            try {
                const url = `${baseUrl}/${session_id}/get-current-page`;
                const response = await axios.get(url);
                msg.current_pages = response.data;

                if (response.data && response.data.length == 1)
                    msg.payload = response.data[0].name;
                else
                    msg.payload = "unknown";

                send(msg);
                if (done) done();
            } catch (err) {
                node.error('Failed to get current page: ' + (err.response?.data?.error || err.message), msg);
                msg.error = err.response?.data?.error || err.message;
                send(msg);
                if (done) done();
            }
        });
    }
    RED.nodes.registerType('browser-get-current-page', BrowserGetCurrentPageNode);
};
