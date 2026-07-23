import { apiFetch } from "./api";

export type Ability = {
  code: string;
  label: string;
  score: number;
  modifier: number;
};

export type Character = {
  id: string;
  campaign_id: string;
  owner_user_id: string;
  name: string;
  race_name: string;
  class_name: string;
  subclass_name: string;
  level: number;
  background: string;
  alignment: string;
  hit_points_current: number;
  hit_points_max: number;
  temporary_hit_points: number;
  armor_class: number;
  initiative: number;
  speed_meters: number;
  abilities: Ability[];
};

type Campaign = {
  id: string;
  name: string;
  ruleset_code: string;
  role: "master" | "player" | "observer";
};

type ListResponse<T> = {
  items: T[];
  next_cursor: null;
};

export type ActiveCharacter = {
  campaign: Campaign;
  character: Character;
};

export async function loadActiveCharacter(): Promise<ActiveCharacter | null> {
  const campaigns = await apiFetch<ListResponse<Campaign>>("/campaigns");
  for (const campaign of campaigns.items) {
    const characters = await apiFetch<ListResponse<Character>>(
      `/campaigns/${campaign.id}/characters`,
    );
    if (characters.items[0]) {
      return { campaign, character: characters.items[0] };
    }
  }
  return null;
}
