from rest_framework import serializers

from .models import Book, Member, Transaction


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['available_copies', 'added_date']

    def validate_isbn(self, value):
        cleaned = value.replace('-', '').replace(' ', '')
        if not cleaned.isdigit():
            raise serializers.ValidationError("ISBN must contain only digits and hyphens.")
        if len(cleaned) not in (10, 13):
            raise serializers.ValidationError("ISBN must be 10 or 13 digits long.")
        return value

    def validate_total_copies(self, value):
        if value < 1:
            raise serializers.ValidationError("Total copies must be at least 1.")
        return value

    def validate_publish_year(self, value):
        if value is not None and (value < 1000 or value > 2100):
            raise serializers.ValidationError("Enter a valid publish year.")
        return value

    def create(self, validated_data):
        validated_data['available_copies'] = validated_data.get('total_copies', 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_total = instance.total_copies
        new_total = validated_data.get('total_copies', old_total)
        if new_total != old_total:
            diff = new_total - old_total
            validated_data['available_copies'] = max(0, instance.available_copies + diff)
        return super().update(instance, validated_data)


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['membership_date']


class TransactionSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['issue_date', 'due_date', 'return_date', 'status', 'fine_amount']
