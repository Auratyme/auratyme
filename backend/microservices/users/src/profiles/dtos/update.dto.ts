export class ProfileUpdateDto {
  userId: string;
  fields?: {
    birthDate?: string | null;
    chronotypeMEQ?: number | null;
  };
}
