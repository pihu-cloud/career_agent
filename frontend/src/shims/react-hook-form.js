import { useState, useRef, useCallback } from 'react';

export const useForm = ({ resolver, defaultValues = {} } = {}) => {
  const [values, setValues] = useState(defaultValues);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const valuesRef = useRef(values);
  valuesRef.current = values;

  const register = useCallback((name, options = {}) => {
    return {
      name,
      value: valuesRef.current[name] ?? '',
      onChange: (e) => {
        let val = e?.target ? (e.target.type === 'checkbox' ? e.target.checked : e.target.value) : e;
        if (options.valueAsNumber) {
          val = val === '' ? '' : Number(val);
        }
        setValues((prev) => {
          const next = { ...prev, [name]: val };
          valuesRef.current = next;
          return next;
        });
      },
      ref: () => {},
    };
  }, []);

  const setValue = useCallback((name, val) => {
    setValues((prev) => {
      const next = { ...prev, [name]: val };
      valuesRef.current = next;
      return next;
    });
  }, []);

  const watch = useCallback((name, fallback) => {
    if (!name) return values;
    return values[name] !== undefined ? values[name] : fallback;
  }, [values]);

  const reset = useCallback((newValues = {}) => {
    setValues(newValues);
    valuesRef.current = newValues;
    setErrors({});
  }, []);

  const handleSubmit = useCallback((onValid, onInvalid) => {
    return async (e) => {
      if (e && e.preventDefault) e.preventDefault();
      setIsSubmitting(true);
      try {
        let currentValues = { ...valuesRef.current };
        let validationErrors = {};

        if (resolver) {
          const res = await resolver(currentValues);
          if (res && res.errors && Object.keys(res.errors).length > 0) {
            validationErrors = res.errors;
            setErrors(validationErrors);
            if (onInvalid) onInvalid(validationErrors);
            setIsSubmitting(false);
            return;
          }
          if (res && res.values) {
            currentValues = res.values;
          }
        }

        setErrors({});
        await onValid(currentValues, e);
      } catch (err) {
        console.error('Submit error:', err);
      } finally {
        setIsSubmitting(false);
      }
    };
  }, [resolver]);

  return {
    register,
    handleSubmit,
    watch,
    reset,
    setValue,
    formState: {
      errors,
      isSubmitting,
    },
  };
};

export default {
  useForm,
};
