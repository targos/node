export function resolve(specifier, context, next) {
  const { url: first } = next(specifier);
  const { url: second } = next(specifier);

  return {
    format: 'module',
    url: first,
  };
}
