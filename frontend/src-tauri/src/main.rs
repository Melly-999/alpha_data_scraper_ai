// MellyTrade desktop thin shell.
//
// Safety posture (must remain true — see tauri.conf.json and the bundled UI):
//   * read-only paper preview only
//   * hosted backend API only (no backend bundled here)
//   * no broker execution, no order/buy/sell/execute controls
//   * no secrets, no account IDs, no custom native command bridge
//
// This binary does nothing more than open a window onto the bundled static
// frontend. It registers no custom Tauri commands and enables no plugins.

// Prevents an extra console window on Windows in release builds. DO NOT REMOVE.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running the MellyTrade desktop shell");
}
