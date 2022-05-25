#!/bin/bash
email="juancepeda.gestion@gmail.com"
username="juanchobanano"
token="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"

helpFunction()
{
   echo ""
   echo "Usage: $0 -a parameterA -b parameterB"
   echo -e "\t-a Git commit comment"
   echo -e "\t-b yes/no whether to upload changes to Heroku"
   exit 1 # Exit script after printing help
}

while getopts "a:b:" opt
do
   case "$opt" in
      a ) parameterA="$OPTARG" ;;
      b ) parameterB="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$parameterA" ] || [ -z "$parameterB" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "$parameterA"
echo "$parameterB"

# Git commands.
#git config --global user.email "$email"
#git config --global user.name "$username"
#git config --global user.password "$token"
#git config --global credential.helper store

git add .
git commit -m "$parameterA"

# Heroku commands.
if [ $parameterB == 'yes' ]
then
   heroku login
   heroku git:remote -a scraper-adultworks
   #git push heroku
fi

# git push
# git push heroku