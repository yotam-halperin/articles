# HOW TO CONFIGURE REPLICATION BETWEEN 2 S3 BUCKETS IN 2 DIFFERENT ACCOUNTS USING AWS DATASYNC:

## create a role in the destination account called 'datasync-role':
* AWS Services
* Use case -> Datasync -> create role
* add permissions -> create inline policy -> JSON:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::<SOURCE_BUCKET>" 
        },
        {
            "Action": [
                "s3:AbortMultipartUpload",
                "s3:DeleteObject",
                "s3:GetObject",
                "s3:ListMultipartUploadParts",
                "s3:PutObject",
                "s3:GetObjectTagging",
                "s3:ListBucket",
                "s3:PutObjectTagging"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::<SOURCE_BUCKET>/*"
        }
    ]
}
* (you can specify * instead of specific source bucket name)

## in the source account, change the source bucket policy:
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Principal": {
    "AWS": [
     "arn:aws:iam::<DESTINATION_ACCOUNT_ID>:role/datasync-role",
     "arn:aws:iam::<DESTINATION_ACCOUNT_ID>:user/<DESTINATION_ACCOUNT_LOGGED_IN_USER>"
    ]
   },
   "Action": [
    "s3:GetBucketLocation",
    "s3:ListBucket",
    "s3:ListBucketMultipartUploads"
   ],
   "Resource": "arn:aws:s3:::<SOURCE_BUCKET>"
  },
  {
   "Effect": "Allow",
   "Principal": {
    "AWS": [
     "arn:aws:iam::<DESTINATION_ACCOUNT_ID>:role/datasync-role",
     "arn:aws:iam::<DESTINATION_ACCOUNT_ID>:user/<DESTINATION_ACCOUNT_LOGGED_IN_USER>"
    ]
   },
   "Action": [
    "s3:AbortMultipartUpload",
    "s3:DeleteObject",
    "s3:GetObject",
    "s3:ListMultipartUploadParts",
    "s3:PutObjectTagging",
    "s3:GetObjectTagging",
    "s3:PutObject"
   ],
   "Resource": "arn:aws:s3:::<SOURCE_BUCKET>/*"
  }
 ]
}

## in the target account change the destination bucket policy:
{
 "Version": "2008-10-17",
 "Statement": [
  {
   "Sid": "DataSyncCreateS3LocationAndTaskAccess",
   "Effect": "Allow",
   "Principal": {
    "AWS": [
     "arn:aws:iam::<DESTINATION_ACCOUNT_ID>:role/datasync-role"
    ]
   },
   "Action": [
    "s3:GetBucketLocation",
    "s3:ListBucket",
    "s3:ListBucketMultipartUploads",
    "s3:AbortMultipartUpload",
    "s3:DeleteObject",
    "s3:GetObject",
    "s3:ListMultipartUploadParts",
    "s3:PutObject",
    "s3:GetObjectTagging",
    "s3:PutObjectTagging"
   ],
   "Resource": [
    "arn:aws:s3:::<DESTINATION_BUCKET>",
    "arn:aws:s3:::<DESTINATION_BUCKET>/*"
   ]
  }
 ]
}

### Now we are ready to use the datasync service:
### we need to create 2 locations: source location, and destination location.
### For destination its not a problem
* location type = s3 -> <DESTINATION_BUCKET>

### For source bucket we can *not* use the UI to create a location from another account so we will use th AWS CLI tool:
aws datasync create-location-s3 --s3-bucket-arn arn:aws:s3:::<SOURCE_BUCKET> --s3-storage-class STANDARD --s3-config BucketAccessRoleArn="arn:aws:iam::<DESTINATION_ACCOUNT_ID>:role/datasync-role" --region <REGION>

### NOW with both the locations we can create a datasync task!!! GOODLUCK