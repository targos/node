{
  'target_defaults': {
    'default_configuration': 'Debug',
    'configurations': {
      # TODO: hoist these out and put them somewhere common, because
      #       RuntimeLibrary MUST MATCH across the entire project
      'Debug': {
        'defines': [ 'DEBUG', '_DEBUG' ],
        'cflags': [ '-Wall', '-Wextra', '-O0', '-g', '-ftrapv' ],
        'msbuild_settings': {
          'ClCompile': {
            'RuntimeLibrary': 'MultiThreadedDebug', # static debug
          },
        },
      },
      'Release': {
        'defines': [ 'NDEBUG' ],
        'cflags': [ '-Wall', '-Wextra', '-O3' ],
        'msvs_build': {
          'ClCompile': {
            'RuntimeLibrary': 'MultiThreaded', # static release
          },
        },
      }
    },
    'msbuild_settings': {
      'ClCompile': {
        # Compile as C++. llhttp.c is actually C99, but C++ is
        # close enough in this case.
        'CompileAs': 'CompileAsCpp',
      },
      'Link': {
        'GenerateDebugInformation': 'true',
      },
    },
    'conditions': [
      ['OS == "win"', {
        'defines': [
          'WIN32'
        ],
      }]
    ],
  },
}
