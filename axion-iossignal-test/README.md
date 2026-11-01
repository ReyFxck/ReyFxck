# AxionOS IosSignal fixed test

Test build of the AxionOS IosSignal RRO.

Changes:
- removes zero-length stroked paths that could render as square blocks;
- uses real filled circles for inactive slots;
- uses filled rounded bars for active signal levels;
- normalizes external size to 24dp;
- keeps all four X positions fixed between signal states;
- package remains `com.android.systemui.signalbar_ar`.

The GitHub Actions workflow builds both debug and release APKs.
