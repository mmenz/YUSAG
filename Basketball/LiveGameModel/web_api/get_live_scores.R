# Parse for live scores: https://urldefense.proofpoint.com/v2/url?u=http-3A__www.espn.com_nba_bottomline_scores&d=CwIFAg&c=-dg2m7zWuuDZ0MUcV7Sdqw&r=cv6aAyZLvfixEIwGTl1CVC--vu6GSSChZibQbI5qo5s&m=8IgGPI2kC0nFd1NUXYWdvoEMWoYfNunolFKZwCjUb0Y&s=P4Cl448K-WH8--R-X4A1dxHtAtNB4D4E1-O5HK82jGU&e=

y <- readLines('http://www.espn.com/nba/bottomline/scores')
y <- strsplit(y,"&nba_s_left")
y <- y[[1]]
y <- gsub("%20", " ", y)
y <- y[grep("^[0-9]", y)]

gameid <- as.numeric(gsub(".*=([0-9][0-9]+).*", "\\1", y))
team1 <- gsub(".*=([A-z ]+[A-z]) [0-9a].*", "\\1", y)
team2 <- gsub("^[0-9]+=[A-z ]+ (at|[0-9]+) ([ ]*)([A-z ]+) [(0-9].*", "\\3", y)
score1 <- as.numeric(gsub(".*=[A-z ]+ ([0-9]+).*", "\\1", y))
score2 <- as.numeric(gsub(".* ([0-9]+) [(].*", "\\1", y))
minrem <- as.numeric(gsub(".*[(]([0-9]+):[0-9]+ I.*", "\\1", y))
secrem <- as.numeric(gsub(".*[(][0-9]+:([0-9]+) I.*", "\\1", y))
timerem <- minrem*60+secrem
qtr <- as.numeric(gsub(".*[(][0-9]+:[0-9]+ IN ([1-4]).*", "\\1", y))

z <- data.frame(gameid=gameid, team1=team1, team2=team2, score1=score1, score2=score2, timerem=timerem, qtr=qtr, stringsAsFactors=FALSE)

write.csv(z, stdout())
