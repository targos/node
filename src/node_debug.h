#pragma once

#if defined(NODE_WANT_INTERNALS) && NODE_WANT_INTERNALS

#ifdef DEBUG
#include "env-inl.h"
#include "util.h"
#include "v8.h"
#endif  // DEBUG

namespace node {
namespace debug {
#ifdef DEBUG
#define TRACK_V8_FAST_API_CALL(options, key)                                   \
  Environment::GetCurrent(options.isolate)->TrackV8FastApiCall(key)
#else  // !DEBUG
#define TRACK_V8_FAST_API_CALL(receiver, key)
#endif  // DEBUG
}  // namespace debug
}  // namespace node

#endif  // defined(NODE_WANT_INTERNALS) && NODE_WANT_INTERNALS
