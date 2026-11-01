package com.reyfxck.axioniossignalpreview;

import de.robv.android.xposed.IXposedHookInitPackageResources;
import de.robv.android.xposed.IXposedHookZygoteInit;
import android.content.res.XModuleResources;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.callbacks.XC_InitPackageResources;

public final class PreviewFixModule implements IXposedHookZygoteInit, IXposedHookInitPackageResources {
    private static final String TARGET = "com.android.axion.axthemestore";
    private static String modulePath;

    @Override
    public void initZygote(StartupParam startupParam) {
        modulePath = startupParam.modulePath;
    }

    @Override
    public void handleInitPackageResources(XC_InitPackageResources.InitPackageResourcesParam resparam) {
        if (!TARGET.equals(resparam.packageName)) return;

        try {
            XModuleResources modRes = XModuleResources.createInstance(modulePath, resparam.res);
            replace(resparam, modRes, "preview_iossignal_1", R.drawable.preview_iossignal_1);
            replace(resparam, modRes, "preview_iossignal_2", R.drawable.preview_iossignal_2);
            replace(resparam, modRes, "preview_iossignal_3", R.drawable.preview_iossignal_3);
            replace(resparam, modRes, "preview_iossignal_4", R.drawable.preview_iossignal_4);
            XposedBridge.log("AxionIosSignalPreviewFix: preview resources replaced");
        } catch (Throwable t) {
            XposedBridge.log("AxionIosSignalPreviewFix failed: " + t);
        }
    }

    private static void replace(
            XC_InitPackageResources.InitPackageResourcesParam resparam,
            XModuleResources modRes,
            String name,
            int moduleDrawable
    ) {
        resparam.res.setReplacement(
                TARGET,
                "drawable",
                name,
                modRes.fwd(moduleDrawable)
        );
    }
}
