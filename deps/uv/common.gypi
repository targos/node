{
  'variables': {
    'target_arch%': 'ia32',          # set v8's target architecture
    'host_arch%': 'ia32',            # set v8's host architecture
    'uv_library%': 'static_library', # allow override to 'shared_library' for DLL/.so builds
    'msvs_multi_core_compile': '0',  # we do enable multicore compiles, but not using the V8 way
  },

  'target_defaults': {
    'default_configuration': 'Debug',
    'configurations': {
      'Debug': {
        'defines': [ 'DEBUG', '_DEBUG' ],
        'cflags': [ '-g' ],
        'msbuild_settings': {
          'ClCompile': {
            'target_conditions': [
              ['uv_library=="static_library"', {
                'RuntimeLibrary': 'MultiThreadedDebug', # /MTd static debug
              }, {
                'RuntimeLibrary': 'MultiThreadedDebugDLL', # /MDd DLL debug
              }],
            ],
            'Optimization': 'Disabled', # /Od, no optimization
            'MinimalRebuild': 'false',
            'OmitFramePointers': 'false',
            'BasicRuntimeChecks': 'EnableFastChecks', # /RTC1
          },
          '': {
            'LinkIncremental': 'true', # enable incremental linking
          },
        },
        'xcode_settings': {
          'GCC_OPTIMIZATION_LEVEL': '0',
        },
        'conditions': [
          ['OS != "zos"', {
            'cflags': [ '-O0', '-fno-common', '-fwrapv' ]
          }],
          ['OS == "android"', {
            'cflags': [ '-fPIE' ],
            'ldflags': [ '-fPIE', '-pie' ]
          }]
        ]
      },
      'Release': {
        'defines': [ 'NDEBUG' ],
        'cflags': [
          '-O3',
        ],
        'msbuild_settings': {
          'ClCompile': {
            'target_conditions': [
              ['uv_library=="static_library"', {
                'RuntimeLibrary': 'MultiThreaded', # /MT static release
              }, {
                'RuntimeLibrary': 'MultiThreadedDLL', # /MD DLL release
              }],
            ],
            'Optimization': 'Full', # /Ox, full optimization
            'FavorSizeOrSpeed': 'Speed', # /Ot, favour speed over size
            'InlineFunctionExpansion': 'AnySuitable', # /Ob2, inline anything eligible
            'WholeProgramOptimization': 'true', # /GL, whole program optimization, needed for LTCG
            'OmitFramePointers': 'true',
            'FunctionLevelLinking': 'true',
            'IntrinsicFunctions': 'true',
          },
          'Lib': {
            'AdditionalOptions': [
              '/LTCG', # link time code generation
            ],
          },
          'Link': {
            'LinkTimeCodeGeneration': 'true', # link-time code generation
            'OptimizeReferences': 'true', # /OPT:REF
            'EnableCOMDATFolding': 'true', # /OPT:ICF
          },
          '': {
            'LinkIncremental': 'false', # disable incremental linking
          },
        },
        'conditions': [
          ['OS != "zos"', {
            'cflags': [
              '-fdata-sections',
              '-ffunction-sections',
              '-fno-common',
              '-fomit-frame-pointer',
            ],
          }],
        ]
      }
    },
    'msbuild_settings': {
      'ClCompile': {
        'StringPooling': 'true', # pool string literals
        'DebugInformationFormat': 'ProgramDatabase', # Generate a PDB
        'WarningLevel': 'Level3',
        'BufferSecurityCheck': 'true',
        'ExceptionHandling': 'Sync', # /EHsc
        'SuppressStartupBanner': 'true',
        'TreatWarningAsError': 'false',
        'AdditionalOptions': [
           '/MP', # compile across multiple CPUs
         ],
      },
      'Lib': {
      },
      'Link': {
        'GenerateDebugInformation': 'true',
        'RandomizedBaseAddress': 'true', # enable ASLR
        'DataExecutionPrevention': 'true', # enable DEP
        'AllowIsolation': 'true',
        'SuppressStartupBanner': 'true',
        'target_conditions': [
          ['_type=="executable"', {
            'SubSystem': 'Console', # console executable
          }],
        ],
      },
    },
    'conditions': [
      ['OS == "win"', {
        'msvs_cygwin_shell': 0, # prevent actions from trying to use cygwin
        'defines': [
          'WIN32',
          # we don't really want VC++ warning us about
          # how dangerous C functions are...
          '_CRT_SECURE_NO_DEPRECATE',
          # ... or that C implementations shouldn't use
          # POSIX names
          '_CRT_NONSTDC_NO_DEPRECATE',
        ],
        'target_conditions': [
          ['target_arch=="x64"', {
            'msvs_configuration_platform': 'x64'
          }]
        ]
      }],
      ['OS in "freebsd dragonflybsd linux openbsd solaris android aix os400"', {
        'cflags': [ '-Wall' ],
        'cflags_cc': [ '-fno-rtti', '-fno-exceptions' ],
        'target_conditions': [
          ['_type=="static_library"', {
            'standalone_static_library': 1, # disable thin archive which needs binutils >= 2.19
          }],
        ],
        'conditions': [
          [ 'host_arch != target_arch and target_arch=="ia32"', {
            'cflags': [ '-m32' ],
            'ldflags': [ '-m32' ],
          }],
          [ 'target_arch=="x32"', {
            'cflags': [ '-mx32' ],
            'ldflags': [ '-mx32' ],
          }],
          [ 'OS=="linux"', {
            'cflags': [ '-ansi' ],
          }],
          [ 'OS=="solaris"', {
            'cflags': [ '-pthreads' ],
            'ldflags': [ '-pthreads' ],
          }],
          [ 'OS not in "solaris android zos"', {
            'cflags': [ '-pthread' ],
            'ldflags': [ '-pthread' ],
          }],
          [ 'OS=="aix" and target_arch=="ppc64"', {
            'cflags': [ '-maix64' ],
            'ldflags': [ '-maix64' ],
          }],
        ],
      }],
      ['OS=="mac"', {
        'xcode_settings': {
          'ALWAYS_SEARCH_USER_PATHS': 'NO',
          'GCC_CW_ASM_SYNTAX': 'NO',                # No -fasm-blocks
          'GCC_DYNAMIC_NO_PIC': 'NO',               # No -mdynamic-no-pic
                                                    # (Equivalent to -fPIC)
          'GCC_ENABLE_CPP_EXCEPTIONS': 'NO',        # -fno-exceptions
          'GCC_ENABLE_CPP_RTTI': 'NO',              # -fno-rtti
          'GCC_ENABLE_PASCAL_STRINGS': 'NO',        # No -mpascal-strings
          'GCC_THREADSAFE_STATICS': 'NO',           # -fno-threadsafe-statics
          'PREBINDING': 'NO',                       # No -Wl,-prebind
          'USE_HEADERMAP': 'NO',
          'WARNING_CFLAGS': [
            '-Wall',
            '-Wendif-labels',
            '-W',
            '-Wno-unused-parameter',
            '-Wstrict-prototypes',
          ],
        },
        'conditions': [
          ['target_arch=="ia32"', {
            'xcode_settings': {'ARCHS': ['i386']},
          }],
          ['target_arch=="x64"', {
            'xcode_settings': {'ARCHS': ['x86_64']},
          }],
        ],
        'target_conditions': [
          ['_type!="static_library"', {
            'xcode_settings': {'OTHER_LDFLAGS': ['-Wl,-search_paths_first']},
          }],
        ],
      }],
     ['OS=="solaris"', {
       'cflags': [ '-fno-omit-frame-pointer' ],
       # pull in V8's postmortem metadata
       'ldflags': [ '-Wl,-z,allextract' ]
     }],
    ],
  },
}
