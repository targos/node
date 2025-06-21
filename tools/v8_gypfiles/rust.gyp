{
  'variables': {
    'RUST_ROOT': '../../deps/v8/third_party/rust',
  },
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
