export type CVProfile = {
  id: string;
  candidate_id: string;
  s3_key: string;
  bucket: string;
  original_filename: string;
  content_type: string;
  file_size_bytes: number | null;
  created_at: string;
  extraction_status: string | null;
  extracted_text: string | null;
  structured_extraction_status: string | null;
  parsed_profile_json: Record<string, unknown> | null;
  structured_extraction_error: string | null;
};

