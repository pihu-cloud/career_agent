export const zodResolver = (schema) => {
  return async (values) => {
    try {
      const result = await schema.safeParseAsync(values);
      if (result.success) {
        return { values: result.data, errors: {} };
      }

      const errors = {};
      if (result.error && result.error.errors) {
        result.error.errors.forEach((err) => {
          const path = err.path.join('.') || 'root';
          if (!errors[path]) {
            errors[path] = {
              type: err.code || 'validation',
              message: err.message,
            };
          }
        });
      }
      return { values: {}, errors };
    } catch (err) {
      return {
        values: {},
        errors: { root: { message: err.message || 'Validation error' } },
      };
    }
  };
};

export default zodResolver;
