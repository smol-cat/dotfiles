if status is-interactive
    # Commands to run in interactive sessions can go here
    alias vim=nvim
    alias vi=nvim

    set -gx ANDROID_PATH /opt/android-sdk
    fish_add_path $ANDROID_PATH/tools
    fish_add_path $ANDROID_PATH/platform-tools
    fish_add_path $ANDROID_PATH/tools/bin
    fish_add_path {$HOME}/.local/bin
    fish_add_path {$HOME}/npm/bin
    set -gx RUST_LOG debug
    set -gx RUST_BACTRACE 1
    set -gx fish_greeting
end
