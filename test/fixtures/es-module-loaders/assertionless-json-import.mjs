const DATA_URL_PATTERN = /^data:application\/json(?:[^,]*?)(;base64)?,([\s\S]*)$/;
const JSON_URL_PATTERN = /\.json(\?[^#]*)?(#.*)?$/;

export function resolve(url, context, next) {
  const resolvedImportAssertions = {}
  if (context.importAssertions.type) {
    resolvedImportAssertions.type = context.importAssertions.type;
  }

  if (resolvedImportAssertions.type == null && (DATA_URL_PATTERN.test(url) || JSON_URL_PATTERN.test(url))) {
    resolvedImportAssertions.type = 'json';
  }

  // Mutation from resolve hook should be discarded.
  context.importAssertions.type = 'whatever';

  return next(url, { ...context, importAssertions: resolvedImportAssertions });
}
