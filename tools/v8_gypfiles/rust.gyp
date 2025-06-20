{
  'variables': {
    'V8_ROOT': '../../deps/v8',
    'RUST_ROOT': '../../deps/v8/third_party/rust',

    # Enable control-flow integrity features, such as pointer authentication
    # for ARM64.
    'v8_control_flow_integrity%': 0,
  },
  'includes': ['toolchain.gypi'],
  'targets': [
    {
      'target_name': 'temporal_capi',
      'type': 'none',
      'direct_dependent_settings': {
        'include_dirs': [
          '<(RUST_ROOT)/chromium_crates_io/vendor/temporal_capi-v0_0_9/bindings/cpp',
        ],
      },
    },
  ],
}
