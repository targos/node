const loaderDataPromises = [];

globalThis.PUSH_SYNC = (data) => {
  loaderDataPromises.push(Promise.resolve(data));
};

globalThis.PUSH_ASYNC = () => {
  let resolve;
  const promise = new Promise((r) => {
    resolve = r;
  });
  loaderDataPromises.push(promise);
  return resolve;
};

export function resolve(specifier, context, next) {
  if (specifier === 'test:loader-data') {
    return {
      format: 'module',
      shortCircuit: true,
      url: specifier,
    };
  }
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === 'test:loader-data') {
    const loaderData = await Promise.all(loaderDataPromises);
    return {
      format: 'module',
      shortCircuit: true,
      source: `export default ${JSON.stringify(loaderData)};\n`,
    };
  }
  return next(url, context);
}
