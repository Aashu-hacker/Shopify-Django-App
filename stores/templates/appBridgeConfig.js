var AppBridge = window['app-bridge'];
var AppBridgeUtils = window['app-bridge-utils'];
var actions = AppBridge.actions;
export var Redirect = actions.Redirect;
const config = {
    // The client ID provided for your application in the Partner Dashboard.
    apiKey: "d97774d41e779fc96ad35d85d8f256ce",
    // The host of the specific shop that's embedding your app. This value is provided by Shopify as a URL query parameter that's appended to your application URL when your app is loaded inside the Shopify admin.
    host: new URLSearchParams(location.search).get("host"),
    forceRedirect: true
};
export const app = AppBridge.createApp(config);