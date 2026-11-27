export interface FormChoice {
  value: string;
  label: string;
}

export interface FormFieldSchema {
  name: string;
  id: string;
  label: string;
  type: string;
  required: boolean;
  disabled: boolean;
  multiple: boolean;
  help_text: string;
  placeholder: string;
  value: string | number | boolean | Array<string | number> | null;
  errors: string[];
  choices: FormChoice[];
}

export interface FormSchema {
  fields: FormFieldSchema[];
  non_field_errors: string[];
}
