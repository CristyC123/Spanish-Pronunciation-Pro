import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FaTrophy } from "react-icons/fa";


function Trophy({ trophy }) {
  const isUnlocked = trophy.unlocked;
  const iconColor = isUnlocked ? "text-yellow-400" : "text-muted-foreground/30";
  const textColor = isUnlocked ? "text-foreground" : "text-muted-foreground/50";

  return (
    <div className="flex items-center space-x-4 p-4 bg-background/50 rounded-lg">
      <FaTrophy className={`text-3xl ${iconColor}`} />
      <div className={textColor}>
        <h3 className="font-bold">{trophy.name}</h3>
        <p className="text-sm">{trophy.description}</p>
      </div>
    </div>
  );
}


export function TrophiesCard({ trophies }) {
  // Filter for unlocked trophies

  return (
    <Card className="col-span-1 lg:col-span-2">
      <CardHeader>
        <CardTitle>Achievements</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {trophies.length > 0 ? ( // Conditional for placeholder
            trophies.map((trophy) => (
              <Trophy key={trophy.id} trophy={trophy} />
            ))
          ) : (
            <p className="col-span-full text-center text-sm text-muted-foreground">
              No achievements unlocked yet. Keep practicing to earn trophies!
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}