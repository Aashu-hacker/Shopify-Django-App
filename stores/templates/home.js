import { app,Redirect } from "./appBridgeConfig";

document.getElementById('view-all-products').onclick = function () {
    console.log(app, Redirect, "pppp")  
    app.dispatch(
        Redirect.toRemote({
            url: '/products'
        })
    );
};