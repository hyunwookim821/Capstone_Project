INSERT INTO "MEMBER" (
  email, password_hash, nickname, job_category, marketing_opt_in, terms_agreed_at, created_at, updated_at
) VALUES
  ('member1@example.com', '$2a$10$2KBHCGRooV900KWUcThpOuTnAJ3jmQk9ihYZzHo73yyxyB94tFc.2', 'member1', NULL, TRUE,  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('member2@example.com', '$2a$10$2KBHCGRooV900KWUcThpOuTnAJ3jmQk9ihYZzHo73yyxyB94tFc.2', 'member2', NULL, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('member3@example.com', '$2a$10$2KBHCGRooV900KWUcThpOuTnAJ3jmQk9ihYZzHo73yyxyB94tFc.2', 'member3', NULL, TRUE,  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
