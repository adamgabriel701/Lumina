; ModuleID = 'primes.ll'
source_filename = "primes.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@__lumina_argc = local_unnamed_addr global i32 0
@__lumina_argv = local_unnamed_addr global ptr null
@str_0 = local_unnamed_addr constant [1 x i8] zeroinitializer
@str_1 = local_unnamed_addr constant [3 x i8] c"%s\00"
@str_2 = local_unnamed_addr constant [2 x i8] c" \00"
@str_3 = constant [4 x i8] c"%ld\00"
@str_4 = local_unnamed_addr constant [2 x i8] c"\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite)
declare noalias noundef ptr @malloc(i64 noundef) local_unnamed_addr #1

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture) local_unnamed_addr #2

declare i64 @atoi(ptr) local_unnamed_addr

define noundef i32 @main(i32 %.1, ptr %.2) local_unnamed_addr {
main_entry:
  store i32 %.1, ptr @__lumina_argc, align 4
  store ptr %.2, ptr @__lumina_argv, align 8
  %argv_elem_ptr = getelementptr ptr, ptr %.2, i64 1
  %argv_elem = load ptr, ptr %argv_elem_ptr, align 8
  %len_str = tail call i64 @strlen(ptr noundef nonnull dereferenceable(1) %argv_elem)
  %icmp = icmp sgt i64 %len_str, 0
  br i1 %icmp, label %if_end, label %for_end.thread38

for_end.thread38:                                 ; preds = %main_entry
  %alloc_bytes_call22 = tail call dereferenceable_or_null(10000000) ptr @malloc(i64 10000000)
  %0 = getelementptr inbounds i8, ptr %alloc_bytes_call22, i64 2
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 1 dereferenceable(9999998) %0, i8 1, i64 9999998, i1 false)
  store i8 0, ptr %alloc_bytes_call22, align 1
  %.2342 = getelementptr i8, ptr %alloc_bytes_call22, i64 1
  store i8 0, ptr %.2342, align 1
  br label %while_body.preheader

if_end:                                           ; preds = %main_entry
  %atoi_call = tail call i64 @atoi(ptr %argv_elem)
  %alloc_bytes_call = tail call ptr @malloc(i64 %atoi_call)
  %for_cond.19 = icmp sgt i64 %atoi_call, 0
  br i1 %for_cond.19, label %for_end, label %for_end.1

for_end:                                          ; preds = %if_end
  tail call void @llvm.memset.p0.i64(ptr align 1 %alloc_bytes_call, i8 1, i64 %atoi_call, i1 false)
  store i8 0, ptr %alloc_bytes_call, align 1
  %.23 = getelementptr i8, ptr %alloc_bytes_call, i64 1
  store i8 0, ptr %.23, align 1
  %icmp.113 = icmp ugt i64 %atoi_call, 4
  br i1 %icmp.113, label %while_body.preheader, label %for_body.1.preheader

while_body.preheader:                             ; preds = %for_end.thread38, %for_end
  %limit.02546 = phi i64 [ 10000000, %for_end.thread38 ], [ %atoi_call, %for_end ]
  %alloc_bytes_call2745 = phi ptr [ %alloc_bytes_call22, %for_end.thread38 ], [ %alloc_bytes_call, %for_end ]
  br label %while_body

while_body:                                       ; preds = %while_body.preheader, %if_end.1
  %mul15 = phi i64 [ %mul, %if_end.1 ], [ 4, %while_body.preheader ]
  %storemerge514 = phi i64 [ %add.1, %if_end.1 ], [ 2, %while_body.preheader ]
  %.28 = getelementptr i8, ptr %alloc_bytes_call2745, i64 %storemerge514
  %ptr_idx_load = load i8, ptr %.28, align 1
  %icmp.2 = icmp eq i8 %ptr_idx_load, 1
  %icmp.311 = icmp slt i64 %mul15, %limit.02546
  %or.cond = and i1 %icmp.2, %icmp.311
  br i1 %or.cond, label %while_body.1, label %if_end.1

for_body.1.preheader:                             ; preds = %if_end.1, %for_end
  %alloc_bytes_call263651 = phi ptr [ %alloc_bytes_call, %for_end ], [ %alloc_bytes_call2745, %if_end.1 ]
  %limit.0243750 = phi i64 [ %atoi_call, %for_end ], [ %limit.02546, %if_end.1 ]
  %min.iters.check = icmp ult i64 %limit.0243750, 4
  br i1 %min.iters.check, label %for_body.1.preheader58, label %vector.ph

vector.ph:                                        ; preds = %for_body.1.preheader
  %n.vec = and i64 %limit.0243750, -4
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %index = phi i64 [ 0, %vector.ph ], [ %index.next, %vector.body ]
  %vec.phi = phi <2 x i64> [ zeroinitializer, %vector.ph ], [ %7, %vector.body ]
  %vec.phi56 = phi <2 x i64> [ zeroinitializer, %vector.ph ], [ %8, %vector.body ]
  %1 = getelementptr i8, ptr %alloc_bytes_call263651, i64 %index
  %2 = getelementptr i8, ptr %1, i64 2
  %wide.load = load <2 x i8>, ptr %1, align 1
  %wide.load57 = load <2 x i8>, ptr %2, align 1
  %3 = icmp eq <2 x i8> %wide.load, <i8 1, i8 1>
  %4 = icmp eq <2 x i8> %wide.load57, <i8 1, i8 1>
  %5 = zext <2 x i1> %3 to <2 x i64>
  %6 = zext <2 x i1> %4 to <2 x i64>
  %7 = add <2 x i64> %vec.phi, %5
  %8 = add <2 x i64> %vec.phi56, %6
  %index.next = add nuw i64 %index, 4
  %9 = icmp eq i64 %index.next, %n.vec
  br i1 %9, label %middle.block, label %vector.body, !llvm.loop !0

middle.block:                                     ; preds = %vector.body
  %bin.rdx = add <2 x i64> %8, %7
  %10 = tail call i64 @llvm.vector.reduce.add.v2i64(<2 x i64> %bin.rdx)
  %cmp.n = icmp eq i64 %limit.0243750, %n.vec
  br i1 %cmp.n, label %for_end.1, label %for_body.1.preheader58

for_body.1.preheader58:                           ; preds = %for_body.1.preheader, %middle.block
  %storemerge620.ph = phi i64 [ 0, %for_body.1.preheader ], [ %n.vec, %middle.block ]
  %add.21719.ph = phi i64 [ 0, %for_body.1.preheader ], [ %10, %middle.block ]
  br label %for_body.1

if_end.1:                                         ; preds = %while_body.1, %while_body
  %add.1 = add i64 %storemerge514, 1
  %mul = mul i64 %add.1, %add.1
  %icmp.1 = icmp slt i64 %mul, %limit.02546
  br i1 %icmp.1, label %while_body, label %for_body.1.preheader

while_body.1:                                     ; preds = %while_body, %while_body.1
  %storemerge812 = phi i64 [ %add, %while_body.1 ], [ %mul15, %while_body ]
  %.33 = getelementptr i8, ptr %alloc_bytes_call2745, i64 %storemerge812
  store i8 0, ptr %.33, align 1
  %add = add i64 %storemerge812, %storemerge514
  %icmp.3 = icmp slt i64 %add, %limit.02546
  br i1 %icmp.3, label %while_body.1, label %if_end.1

for_body.1:                                       ; preds = %for_body.1.preheader58, %for_body.1
  %storemerge620 = phi i64 [ %for_next.1, %for_body.1 ], [ %storemerge620.ph, %for_body.1.preheader58 ]
  %add.21719 = phi i64 [ %spec.select, %for_body.1 ], [ %add.21719.ph, %for_body.1.preheader58 ]
  %.45 = getelementptr i8, ptr %alloc_bytes_call263651, i64 %storemerge620
  %ptr_idx_load.1 = load i8, ptr %.45, align 1
  %icmp.4 = icmp eq i8 %ptr_idx_load.1, 1
  %add.2 = zext i1 %icmp.4 to i64
  %spec.select = add i64 %add.21719, %add.2
  %for_next.1 = add nuw nsw i64 %storemerge620, 1
  %exitcond.not = icmp eq i64 %for_next.1, %limit.0243750
  br i1 %exitcond.not, label %for_end.1, label %for_body.1, !llvm.loop !3

for_end.1:                                        ; preds = %for_body.1, %middle.block, %if_end
  %add.217.lcssa = phi i64 [ 0, %if_end ], [ %10, %middle.block ], [ %spec.select, %for_body.1 ]
  %putchar = tail call i32 @putchar(i32 32)
  %print_call.1 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_3, i64 %add.217.lcssa)
  %putchar7 = tail call i32 @putchar(i32 10)
  ret i32 0
}

; Function Attrs: nofree nounwind
declare noundef i32 @putchar(i32 noundef) local_unnamed_addr #0

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.vector.reduce.add.v2i64(<2 x i64>) #4

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite) "alloc-family"="malloc" }
attributes #2 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #3 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!0 = distinct !{!0, !1, !2}
!1 = !{!"llvm.loop.isvectorized", i32 1}
!2 = !{!"llvm.loop.unroll.runtime.disable"}
!3 = distinct !{!3, !2, !1}
