import React, { useState, useRef, useCallback } from 'react';

export const useDropzone = ({ onDrop, accept, maxSize = Infinity, multiple = false } = {}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const inputRef = useRef(null);

  const handleFiles = useCallback((filesList) => {
    const files = Array.from(filesList);
    const accepted = [];
    const rejected = [];

    files.forEach((file) => {
      let isAccepted = true;
      let rejectError = null;

      if (maxSize && file.size > maxSize) {
        isAccepted = false;
        rejectError = { code: 'file-too-large', message: 'File is larger than maximum allowed size' };
      }

      if (accept) {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        const mime = file.type;
        const validExts = Object.values(accept).flat();
        const validMimes = Object.keys(accept);

        const extMatch = validExts.includes(ext);
        const mimeMatch = validMimes.includes(mime);

        if (!extMatch && !mimeMatch) {
          isAccepted = false;
          rejectError = { code: 'file-invalid-type', message: 'File type not accepted' };
        }
      }

      if (isAccepted) {
        accepted.push(file);
      } else {
        rejected.push({ file, errors: [rejectError] });
      }
    });

    if (onDrop) {
      onDrop(accepted, rejected);
    }
  }, [onDrop, accept, maxSize]);

  const getRootProps = useCallback((props = {}) => ({
    ...props,
    onDragOver: (e) => {
      e.preventDefault();
      setIsDragActive(true);
      if (props.onDragOver) props.onDragOver(e);
    },
    onDragLeave: (e) => {
      e.preventDefault();
      setIsDragActive(false);
      if (props.onDragLeave) props.onDragLeave(e);
    },
    onDrop: (e) => {
      e.preventDefault();
      setIsDragActive(false);
      if (e.dataTransfer && e.dataTransfer.files) {
        handleFiles(e.dataTransfer.files);
      }
      if (props.onDrop) props.onDrop(e);
    },
    onClick: (e) => {
      if (inputRef.current) {
        inputRef.current.click();
      }
      if (props.onClick) props.onClick(e);
    },
  }), [handleFiles]);

  const getInputProps = useCallback((props = {}) => ({
    ...props,
    ref: inputRef,
    type: 'file',
    style: { display: 'none' },
    multiple,
    onChange: (e) => {
      if (e.target && e.target.files) {
        handleFiles(e.target.files);
      }
      if (props.onChange) props.onChange(e);
    },
  }), [handleFiles, multiple]);

  const open = useCallback(() => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  }, []);

  return {
    getRootProps,
    getInputProps,
    isDragActive,
    open,
  };
};

export default {
  useDropzone,
};
