#include "node_debug.h"

#ifdef DEBUG
#include "node_binding.h"

#include "env.h"
#include "util.h"
#include "v8-fast-api-calls.h"
#include "v8.h"
#endif  // DEBUG

namespace node {
namespace debug {

#ifdef DEBUG
using v8::Context;
using v8::FastApiCallbackOptions;
using v8::FunctionCallbackInfo;
using v8::Local;
using v8::Number;
using v8::Object;
using v8::String;
using v8::Value;

void GetV8FastApiCallCount(const FunctionCallbackInfo<Value>& args) {
  Environment* env = Environment::GetCurrent(args);
  if (!args[0]->IsString()) {
    env->ThrowError("getV8FastApiCallCount must be called with a string");
    return;
  }
  Local<String> name = args[0].As<String>();
  Utf8Value utf8_name(env->isolate(), name);
  args.GetReturnValue().Set(env->GetV8FastApiCallCount(utf8_name.ToString()));
}

void SlowIsEven(const FunctionCallbackInfo<Value>& args) {
  Environment* env = Environment::GetCurrent(args);
  if (!args[0]->IsNumber()) {
    env->ThrowError("isEven must be called with a number");
    return;
  }
  int64_t value = args[0].As<Number>()->Value();
  args.GetReturnValue().Set(value % 2 == 0);
}

bool FastIsEven(Local<Value> receiver,
                const int64_t value,
                // NOLINTNEXTLINE(runtime/references)
                FastApiCallbackOptions& options) {
  TRACK_V8_FAST_API_CALL(options, "debug.isEven");
  return value % 2 == 0;
}

void SlowIsOdd(const FunctionCallbackInfo<Value>& args) {
  Environment* env = Environment::GetCurrent(args);
  if (!args[0]->IsNumber()) {
    env->ThrowError("isOdd must be called with a number");
    return;
  }
  int64_t value = args[0].As<Number>()->Value();
  args.GetReturnValue().Set(value % 2 != 0);
}

bool FastIsOdd(Local<Value> receiver,
               const int64_t value,
               // NOLINTNEXTLINE(runtime/references)
               FastApiCallbackOptions& options) {
  TRACK_V8_FAST_API_CALL(options, "debug.isOdd");
  return value % 2 != 0;
}

static v8::CFunction fast_is_even(v8::CFunction::Make(FastIsEven));
static v8::CFunction fast_is_odd(v8::CFunction::Make(FastIsOdd));

void Initialize(Local<Object> target,
                Local<Value> unused,
                Local<Context> context,
                void* priv) {
  SetMethod(context, target, "getV8FastApiCallCount", GetV8FastApiCallCount);
  SetFastMethod(context, target, "isEven", SlowIsEven, &fast_is_even);
  SetFastMethod(context, target, "isOdd", SlowIsOdd, &fast_is_odd);
}
#endif  // DEBUG

}  // namespace debug
}  // namespace node

#ifdef DEBUG
NODE_BINDING_CONTEXT_AWARE_INTERNAL(debug, node::debug::Initialize)
#endif  // DEBUG
