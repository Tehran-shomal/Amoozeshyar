import type { FormSchema } from "../forms/types";

export interface NavigationItem {
  label: string;
  slug: string;
  icon: string;
}

export interface NavigationGroup {
  title: string;
  items: NavigationItem[];
}

export interface PortalShellData {
  nav_groups: NavigationGroup[];
  sidebar_footer: Array<{
    label: string;
    slug: string;
    icon: string;
    action?: boolean;
  }>;
  profiles: Array<{ student_code: string; educational_level: string }>;
  current_profile: {
    student_code: string;
    full_name: string;
    field_name: string;
    educational_level: string;
  } | null;
  student: {
    name?: string;
    avatar_initials?: string;
    student_code?: string;
    term?: string;
  };
  profile_notice: string;
  term_options: Array<{
    value: string;
    display_label: string;
    selected: boolean;
  }>;
}

export interface PagePayload {
  schema_version: 1;
  page: string;
  title: string;
  subtitle: string;
  owner: string;
  profile: { student_code: string | null };
  term: { term_code: string | null; display_label: string };
  shell: PortalShellData;
  data: Record<string, unknown>;
  form: FormSchema | null;
  omitted_fields: string[];
}

export interface ApiErrorBody {
  code: string;
  message: string;
}

export interface SubmitResult {
  redirect?: string;
  error?: ApiErrorBody;
  form?: FormSchema | null;
}

export interface CourseOffering {
  id: number;
  term_id: number;
  lesson_code: string;
  title: string;
  theory_units: number;
  practical_units: number;
  total_units: number;
  teacher: string;
  day_of_week: string | null;
  start_time: string;
  end_time: string;
  classroom: { building: string; room: string };
  capacity: number;
  remaining_capacity: number;
  exam_date: string | null;
  exam_time: string | null;
}

export interface EnrollmentApiResult {
  enrollment: {
    id: number;
    student_code: string;
    offering_id: number;
    lesson_code: string;
    lesson_title: string;
    status: string | null;
    enrollment_date: string;
    drop_date: string | null;
  };
  created?: boolean;
}
