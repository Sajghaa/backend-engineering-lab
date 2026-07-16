import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column({ unique: true })
  username: string;

  @Column()
  hashedPassword: string;

  @Column({ default: true })
  isActive: boolean;

  @Column({ default: 'user' })
  role: string;
}
