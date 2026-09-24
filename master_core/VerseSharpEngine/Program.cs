using Renzoverse.BotWars.Core;

var match = new MatchManager();
match.Start();

while (true)
{
    match.Update(0.1f);
    Thread.Sleep(100);
}
