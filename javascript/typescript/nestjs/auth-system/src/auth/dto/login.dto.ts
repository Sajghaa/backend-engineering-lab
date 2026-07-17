import { ApiProperty } from '@nestjs/swagger';

export class LoginDto {
  @ApiProperty({ example: 'johndoe' })
  username: string;

  @ApiProperty({ example: 'secret123' })
  password: string;
}
